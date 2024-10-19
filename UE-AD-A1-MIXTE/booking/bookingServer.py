import grpc
from concurrent import futures
from booking import run_movie_check_for_date
import booking_pb2
import booking_pb2_grpc
import json

class BookingServicer(booking_pb2_grpc.BookingServicer):

    def __init__(self):
        with open('{}/data/bookings.json'.format("."), "r") as jsf:
            self.db = json.load(jsf)["bookings"]

    # utility function : write changes to bookings.json database
    def write(self, bookings):
        with open('{}/data/bookings.json'.format("."), 'w') as f:
            json.dump({"bookings" : bookings}, f)

    def GetBookingByUserID(self, request, context):
        for booking in self.db:
            if booking['userid'] == request.id:
                print("User found!")
                user_schedule_list = []
                for date_entry in booking['dates']:
                    user_schedule = booking_pb2.DateSchedule(date=date_entry['date'], movies=date_entry['movies'])
                    user_schedule_list.append(user_schedule)
                return booking_pb2.UserBooking(userid=booking['userid'], schedule=user_schedule_list)
        context.set_code(grpc.StatusCode.NOT_FOUND)
        context.set_details('User has no bookings')
        return booking_pb2.UserBooking(userid="", schedule=[])

    def GetBookings(self, request, context):
        print("All bookings")
        for booking in self.db:
            user_schedule_list = []
            for date_entry in booking['dates']:
                user_schedule = booking_pb2.DateSchedule(date=date_entry['date'], movies=date_entry['movies'])
                user_schedule_list.append(user_schedule)
            yield booking_pb2.UserBooking(userid=booking['userid'], schedule=user_schedule_list)

    def AddBookingToUser(self, request, context):
        print("post request")
        print(request.schedule[0].date)
        showtime = run_movie_check_for_date(request.schedule[0].date)
        movie_id = request.schedule[0].movies[0]
        print("check")
        if movie_id not in showtime.movies:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details('Movie not shown on this day')
            raise ValueError("Movie not available on that day")
        for booking in self.db:
            print("am i here")
            if booking['userid'] == request.userid:
                print("ok1")
                for date in booking['dates']:
                    print("ok2")
                    if date["date"] == request.schedule[0].date:
                        print("ok3")
                        if movie_id in date["movies"]:
                            print('booking already registered')
                            context.set_code(grpc.StatusCode.ALREADY_EXISTS)
                            context.set_details('Booking already registered')
                            raise ValueError("Booking already registered")
                        else : 
                            print("adding booking in date")
                            date["movies"].append(movie_id)
                            self.write(self.db)
                            user_schedule_list = []
                            for date_entry in booking['dates']:
                                user_schedule = booking_pb2.DateSchedule(date=date_entry['date'], movies=date_entry['movies'])
                                user_schedule_list.append(user_schedule)
                            return booking_pb2.UserBooking(userid=booking['userid'], schedule=user_schedule_list)
                booking["dates"].append({
                "date" : request.schedule[0].date,
                "movies" : [movie_id]
            })
                print("adding date")
                self.write(self.db)
                userSchedule = booking_pb2.DateSchedule(date=request.schedule[0].date,movies=[movie_id])
                return booking_pb2.UserBooking(userid=booking['userid'], schedule=[userSchedule])
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
    
    def GetScheduleByDate(self, request, context):
        print(request.date)
        showtime = run_movie_check_for_date(request.date)
        return showtime

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    booking_pb2_grpc.add_BookingServicer_to_server(BookingServicer(), server)
    server.add_insecure_port('[::]:3003')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    serve()
