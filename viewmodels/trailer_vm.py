from services.trailer_service import TrailerService


class TrailerViewModel:

    def get_trailers(self):
        trailers = TrailerService.get_all_trailers()

        result = []
        for t in trailers:
            result.append({
                "name": t.name,
                "description": t.description,
                "price_full_day": t.price_full_day
            })

        return result