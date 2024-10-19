import grpc

import booking_pb2
import booking_pb2_grpc


def get_booking_by_user(stub,userid):
    try :
        booking = stub.GetBookingByUserID(userid)
        print(booking.userid)
        for date in booking.schedule :
            print(date.date)
            for movie in date.movies:
                print(movie)
            print('-------------------------')
        return booking 
    except grpc.RpcError as e:
        if e.code() == grpc.StatusCode.NOT_FOUND:
            return 404 #Code erreur lorsque le user n'est pas trouvé

def get_bookings(stub):
    allbookings = stub.GetBookings(booking_pb2.Empty())
    for booking in allbookings:
        print("----------------------")
        print(booking.userid)
        for date in booking.schedule :
            print(date.date)
            for movie in date.movies:
                print(movie)
            print('-------------------------')
    return allbookings

def add_booking(stub,userbooking):
    try :
        booking = stub.AddBookingToUser(userbooking)
        
        print(booking.userid)
        for date in booking.schedule :
            print(date.date)
            for movie in date.movies:
                print(movie)
        return booking
    except grpc.RpcError as e:
        print(e)
        if e.code() == grpc.StatusCode.NOT_FOUND:
            return 404 #Movie not found on this date
        if e.code() == grpc.StatusCode.ALREADY_EXISTS:
            return 405 #Code error for booking already existing

def get_schedule_by_date(stub,date):
    schedule = stub.GetScheduleByDate(date)
    print(schedule.date)
    for movie in schedule.movies :
        print(movie)
    return schedule



def run():
    # NOTE(gRPC Python Team): .close() is possible on a channel and should be
    # used in circumstances in which the with statement does not fit the needs
    # of the code.
    with grpc.insecure_channel('localhost:3003') as channel:
        stub = booking_pb2_grpc.BookingStub(channel)

        print("-------------- GetBookingByUserID --------------")
        user_id = booking_pb2.UserID(id="d")
        get_booking_by_user(stub, user_id)
        print("-------------- GetBookings ---------------------")
        get_bookings(stub)
        print("-------------- PostBooking ---------------------")
        date_schedule = booking_pb2.DateSchedule(date="20151202", movies = ["96798c08-d19b-4986-a05d-7da856efb697"])
        print(date_schedule.date)
        userschedule = [date_schedule]
        userbooking = booking_pb2.UserBooking(userid="chovy_wins_worlds", schedule = userschedule)
        add_booking(stub, userbooking)

    channel.close()

def run_get_bookings_by_userid(userid):
    # NOTE(gRPC Python Team): .close() is possible on a channel and should be
    # used in circumstances in which the with statement does not fit the needs
    # of the code.
    with grpc.insecure_channel('localhost:3003') as channel:
        stub = booking_pb2_grpc.BookingStub(channel)

        print("-------------- GetBookingByUserID --------------")
        user_id = booking_pb2.UserID(id=userid)
        bookings = get_booking_by_user(stub, user_id)
        return bookings
    channel.close()

def run_add_booking_user(userid,request):
    # NOTE(gRPC Python Team): .close() is possible on a channel and should be
    # used in circumstances in which the with statement does not fit the needs
    # of the code.
    with grpc.insecure_channel('localhost:3003') as channel:
        stub = booking_pb2_grpc.BookingStub(channel)
        
        print("-------------- PostBooking ---------------------")
        date_schedule = booking_pb2.DateSchedule(date=request["date"], movies = [request["movieid"]])
        userschedule = [date_schedule]
        userbooking = booking_pb2.UserBooking(userid=userid, schedule = userschedule)
        booking = add_booking(stub, userbooking)
        return booking

    channel.close()

def get_schedule_date(date):
    # NOTE(gRPC Python Team): .close() is possible on a channel and should be
    # used in circumstances in which the with statement does not fit the needs
    # of the code.
    with grpc.insecure_channel('localhost:3003') as channel:
        stub = booking_pb2_grpc.BookingStub(channel)
        
        print("-------------- GetScheduleByDate ---------------------")
        date_schedule = booking_pb2.DateString(date=date)
        schedule = get_schedule_by_date(stub, date_schedule)
        return schedule

    channel.close()

if __name__ == '__main__':
    run()
