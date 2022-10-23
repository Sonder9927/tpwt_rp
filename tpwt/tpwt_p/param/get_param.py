import demjson

# param class
class Param:

    def __init__(self, p: dict) -> None:
        self.targets = p["targets"]
        self.filter = p["filter"]
        self.model = p["model"]
        self.inverse = p["model"]

    def __str__(self):
        return "This is a parameters class."


# json
def get_param_json(json_file):
    """
    Get parameters from json data file.
    """
    return Param(demjson.decode_file(json_file))


if __name__ == "__main__":
    print(get_param_json("param.json"))
