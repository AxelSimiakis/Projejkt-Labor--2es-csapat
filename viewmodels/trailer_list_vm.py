from services.trailer_service import TrailerService


class TrailerListViewModel:

    def get_all_trailers(self):
        return TrailerService.get_all_trailers()