from dataclasses import dataclass

CPE_VERSION = 2.3

@dataclass
class App:
    name: str
    vendor: str
    version: str

    def __post_init__(self):
        self.cpe = self.get_cpe()

    def get_cpe(self):
        # TODO: add description of CPE
        # TODO: fuzzy string matching to match vendors/products to valid ones in CPE (ex: map "Microsoft Corporation" -> "microsoft")
        vendor = self.vendor.lower()
        product = self.name.lower()
        version = self.version()
        return f"cpe:{CPE_VERSION}:a:{vendor}:{product}:{version}:*:*:*:*:*:*"