from views.trailer_list_view import TrailerListView


class TrailerView(TrailerListView):
    """
    Kompatibilitási réteg a régi importokhoz.

    Ha a projekt más része még a TrailerView osztályt importálja,
    akkor ez ugyanazt a működést adja vissza, mint a TrailerListView.
    """

    def __init__(self, main_window=None, user=None):
        super().__init__(main_window=main_window)
        self.user = user