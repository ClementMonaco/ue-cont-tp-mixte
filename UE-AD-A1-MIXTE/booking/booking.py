import grpc

import showtime_pb2
import showtime_pb2_grpc

# The service Booking is calling the Showtime service via the gRPC API. 
# This file is the client Booking code for calling Showtime. > see showtime/showtime.py

def get_showtime_by_date(stub,date):
    schedule = stub.GetShowtimeByDate(date)
    print(schedule.date)
    for movie in schedule.movies :
        print(movie)
    return schedule

def get_showtimes(stub):
    allschedule = stub.GetShowtimes(showtime_pb2.EmptySchedule())
    for schedule in allschedule:
        print("----------------------")
        print(schedule.date)
        for movie in schedule.movies :
            print(movie)
    return allschedule

# hardcoded tests for debug
def run():
    # NOTE(gRPC Python Team): .close() is possible on a channel and should be
    # used in circumstances in which the with statement does not fit the needs
    # of the code.
    with grpc.insecure_channel('localhost:3002') as channel:
        stub = showtime_pb2_grpc.ShowtimeStub(channel)

        print("-------------- GetShowtimeByDate --------------")
        date = showtime_pb2.Date(date="20151130")
        get_showtime_by_date(stub, date)
        print("-------------- GetShowtimes -------------------")
        get_showtimes(stub)

    channel.close()

# function to open a communication with the Showtime service and get the showtimes by passing in a date
def run_movie_check_for_date(date):
    # NOTE(gRPC Python Team): .close() is possible on a channel and should be
    # used in circumstances in which the with statement does not fit the needs
    # of the code.
    with grpc.insecure_channel('localhost:3002') as channel:
        stub = showtime_pb2_grpc.ShowtimeStub(channel)
        _date = showtime_pb2.Date(date=date)
        booking = get_showtime_by_date(stub, _date)
        return booking

    channel.close()

if __name__ == '__main__':
    run()
