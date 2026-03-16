from services.trailer_service import TrailerService


class TrailerViewModel:

    def get_trailers(self):
        trailers = TrailerService.get_all_trailers()

        result = []
        for t in trailers:
            result.append({
                "id": t.id,
                "name": t.name,
                "description": t.description,
                "price_morning": t.price_morning,
                "price_afternoon": t.price_afternoon,
                "price_full_day": t.price_full_day,
                "deposit": t.deposit,
            })

        return result