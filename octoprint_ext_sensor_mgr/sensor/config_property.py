from dataclasses import asdict, dataclass

@dataclass
class ConfigProperty:
    data_type: type
    value_list: list
    default_value: any
    label: str
    group_seq: tuple[str, ...]

    def __init__(self, data_type: type, value_list: list, default_value: any, label: str, group_seq: tuple[str, ...] = None):
        self.data_type = data_type
        self.value_list = value_list
        self.default_value = default_value
        self.label = label
        self.group_seq = group_seq
        
    def to_dict(self):
        return asdict(self)