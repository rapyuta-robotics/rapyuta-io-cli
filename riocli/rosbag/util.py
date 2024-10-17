class ROSBagJobNotFound(Exception):
    def __init__(self, message="rosbag job not found"):
        self.message = message
        super().__init__(self.message)
