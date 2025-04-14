import json

config_file = 'config.json'

class Config:
    def __init__(self) -> None:
        self.science_parse_api_host = ''
        self.science_parse_api_port = ''
        self.upload_dir = ''
        self.model_name = ''
        self.model_type = ''
        self.zone_model = ''
        self.similarity_threshold = 0
        self.__read_file(config_file)

    def __read_file(self, file_name: str):
        with open(file_name) as input_file:
            config_data = json.load(input_file)
            self.science_parse_api_host = config_data['SCIENCE_PARSE_API_HOST']
            self.science_parse_api_port = config_data['SCIENCE_PARSE_API_PORT']
            self.upload_dir = config_data['UPLOAD_DIR']
            self.model_name = config_data['MODEL_NAME']
            self.model_type = config_data['MODEL_TYPE']
            self.zone_model = config_data['ZONE_MODEL']
            self.similarity_threshold = config_data['SIMILARITY_THRESHOLD']

    def __str__(self) -> str:
        return f"Science Parse API Host: {self.science_parse_api_host}\nScience Parse API Port: {self.science_parse_api_port}\nUpload Directory: {self.upload_dir}"

class ConfigManager:
    def __init__(self) -> None:
        self.config = Config()

# config = ConfigManager().config

# if __name__ == '__main__':
#     config = ConfigManager().config
#     print(config)