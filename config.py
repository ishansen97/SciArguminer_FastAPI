import json

config_file = 'config.json'

class Config:
    def __init__(self) -> None:
        self.science_parse_api_host = ''
        self.science_parse_api_port = ''
        self.upload_dir = ''
        self.bart_model = ''
        self.__read_file(config_file)

    def __read_file(self, file_name: str):
        with open(file_name) as input_file:
            config_data = json.load(input_file)
            self.science_parse_api_host = config_data['SCIENCE_PARSE_API_HOST']
            self.science_parse_api_port = config_data['SCIENCE_PARSE_API_PORT']
            self.upload_dir = config_data['UPLOAD_DIR']
            self.bart_model = config_data['BART_MODEL']

    def __str__(self) -> str:
        return f"Science Parse API Host: {self.science_parse_api_host}\nScience Parse API Port: {self.science_parse_api_port}\nUpload Directory: {self.upload_dir}"

class ConfigManager:
    def __init__(self) -> None:
        self.config = Config()

# config = ConfigManager().config

# if __name__ == '__main__':
#     config = ConfigManager().config
#     print(config)