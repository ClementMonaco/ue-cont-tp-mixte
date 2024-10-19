import grpc
from concurrent import futures
from booking import run_movie_check_for_date
import booking_pb2
import booking_pb2_grpc
import json

# The service Booking is also a gRPC server called by service User 
# Here we define the services provided by the Booking server

class BookingServicer(booking_pb2_grpc.BookingServicer):

    def __init__(self):
        with open('{}/data/bookings.json'.format("."), "r") as jsf:
            self.db = json.load(jsf)["bookings"]

    # utility function : write changes to bookings.json database
    def write(self, bookings):
        with open('{}/data/bookings.json'.format("."), 'w') as f:
            json.dump({"bookings" : bookings}, f)

    # get bookings by passing in a user id
    def GetBookingByUserID(self, request, context):
        for booking in self.db:
            if booking['userid'] == request.id:
                print("User found!")
                user_schedule_list = []
                for date_entry in booking['dates']:
                    # create a DateSchedule object > see booking proto
                    user_schedule = booking_pb2.DateSchedule(date=date_entry['date'], movies=date_entry['movies'])
                    user_schedule_list.append(user_schedule)
                return booking_pb2.UserBooking(userid=booking['userid'], schedule=user_schedule_list)
        # set gRPC error code accordingly
        context.set_code(grpc.StatusCode.NOT_FOUND)
        context.set_details('User has no bookings')
        # return a UserBooking object > see Booking proto
        return booking_pb2.UserBooking(userid="", schedule=[])

    # get all bookings 
    def GetBookings(self, request, context):
        print("All bookings")
        for booking in self.db:
            user_schedule_list = []
            for date_entry in booking['dates']:
                user_schedule = booking_pb2.DateSchedule(date=date_entry['date'], movies=date_entry['movies'])
                user_schedule_list.append(user_schedule)
            yield booking_pb2.UserBooking(userid=booking['userid'], schedule=user_schedule_list)

    # add a booking for a user to the bookings db
    def AddBookingToUser(self, request, context):
        # prints for clarity and debug
        print("post request")
        print(request.schedule[0].date)
        # call to the showtime service to check that the date exists and the desired movie is on air at this date
        showtime = run_movie_check_for_date(request.schedule[0].date)
        movie_id = request.schedule[0].movies[0]
        print("check")
        if movie_id not in showtime.movies:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details('Movie not shown on this day')
            raise ValueError("Movie not available on that day")
        for booking in self.db:
            if booking['userid'] == request.userid:
                # if the user already has bookings in the db
                for date in booking['dates']:
                    # if they already have bookings on this day
                    if date["date"] == request.schedule[0].date:
                        if movie_id in date["movies"]:
                            # if the booking already exists
                            print('booking already registered')
                            context.set_code(grpc.StatusCode.ALREADY_EXISTS)
                            context.set_details('Booking already registered')
                            raise ValueError("Booking already registered")
                        else : 
                            # add the booking to the db
                            print("adding booking in date")
                            date["movies"].append(movie_id)
                            self.write(self.db)
                            user_schedule_list = []
                            for date_entry in booking['dates']:
                                user_schedule = booking_pb2.DateSchedule(date=date_entry['date'], movies=date_entry['movies'])
                                user_schedule_list.append(user_schedule)
                            return booking_pb2.UserBooking(userid=booking['userid'], schedule=user_schedule_list)
                # if the user does not have bookings on this day yet
                booking["dates"].append({
                "date" : request.schedule[0].date,
                "movies" : [movie_id]
            })
                print("adding date")
                self.write(self.db)
                userSchedule = booking_pb2.DateSchedule(date=request.schedule[0].date,movies=[movie_id])
                return booking_pb2.UserBooking(userid=booking['userid'], schedule=[userSchedule])
        # if the user has no bookings yet
        self.db.append({
      "userid": request.userid,
      "dates": [
        {
          "date": request.schedule[0].date,
          "movies": [movie_id]
        }
      ]
    })
        print("adding user in bookings")
        self.write(self.db)
        userSchedule = booking_pb2.DateSchedule(date=request.schedule[0].date,movies=[movie_id])
        return booking_pb2.UserBooking(userid=request.userid, schedule=[userSchedule])
        return booking_pb2.UserBooking(userid="", schedule=[])

    # get the showtimes by passing in a date
    def GetScheduleByDate(self, request, context):
        print(request.date)
        showtime = run_movie_check_for_date(request.date)
        return showtime
# gRPC server definition and start
def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    booking_pb2_grpc.add_BookingServicer_to_server(BookingServicer(), server)
    server.add_insecure_port('[::]:3003')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    serve()
