class CommandContextMixin:
    title = None

    def get_context_data(self, **kwargs):
        context = super(CommandContextMixin, self).get_context_data(**kwargs)
        context['title'] = self.title
        return context
