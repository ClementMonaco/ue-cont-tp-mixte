import grpc
from concurrent import futures
import showtime_pb2
import showtime_pb2_grpc
import json

class ShowtimeServicer(showtime_pb2_grpc.ShowtimeServicer):

    def __init__(self):
        with open('{}/data/times.json'.format("."), "r") as jsf:
            self.db = json.load(jsf)["schedule"]

    def GetShowtimeByDate(self, request, context):
        for date in self.db:
            if date['date'] == str(request.date):
                print("Date found!")
                return showtime_pb2.Schedule(date=date['date'], movies=date['movies'])
        return showtime_pb2.Schedule(date="", movies=[])

    def GetShowtimes(self, request, context):
        for date in self.db:
            yield showtime_pb2.Schedule(date=date['date'], movies=date['movies'])

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    showtime_pb2_grpc.add_ShowtimeServicer_to_server(ShowtimeServicer(), server)
    server.add_insecure_port('[::]:3002')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    serve()
