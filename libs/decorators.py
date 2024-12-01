def save_screnshot(func):
    def wrapper(self, *args, **kwargs):
        # Take a screenshot of current chrome window
        self.screenshot("screenshot.png")

        result = func(self, *args, **kwargs)

        return result
    return wrapper
