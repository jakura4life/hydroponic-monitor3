from django.conf import settings
EMA_ALPHA = settings.EMA_ALPHA

class EMASmoother:
    def __init__(self, alpha=EMA_ALPHA):
        self.alpha = alpha
        self.ema = None

    def update(self, value):
        if self.ema is None:
            self.ema = value
        else:
            self.ema = self.alpha * value + (1 - self.alpha) * self.ema
        return self.ema
    
