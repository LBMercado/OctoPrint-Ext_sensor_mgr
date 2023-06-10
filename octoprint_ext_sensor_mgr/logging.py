from enum import Flag, auto


class ContextLevel(Flag):
    DEBUG = auto()
    ERROR = auto()
    WARNING = auto()


class Logging:
    def __init__(self, logger: None = None, enable_debug=False):
        self.logger = logger  # ignored, use native print() always
        self.enable_debug = enable_debug

    def _debug(self, text: str, context_level: ContextLevel):
        print(text)

    def debug(self, context: str, ref_object: object = None, context_level: ContextLevel = ContextLevel.DEBUG):
        if ref_object is not None:
            text = context + ": " + str(ref_object)
        else:
            text = context
        if self.enable_debug:
            self._debug(text, context_level)
        return text


class OctoprintLogging(Logging):
    def __init__(self, logger, enable_debug=False):
        super().__init__(logger, enable_debug)

    def _debug(self, text: str, context_level: ContextLevel):
        if ContextLevel.DEBUG & context_level:
            self.logger.debug(text)
        elif ContextLevel.WARNING & context_level:
            self.logger.warning(text)
        elif ContextLevel.ERROR & context_level:
            self.logger.error(text)
