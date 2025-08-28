import json, os

class LocalMemory:
    def __init__(self, file_path="memory.json"):
        self.file_path = file_path
        if not os.path.exists(self.file_path):
            with open(self.file_path, "w") as f:
                json.dump({"facts": {}, "credentials": {}}, f)

    def _load(self):
        with open(self.file_path, "r") as f:
            return json.load(f)

    def _save(self, data):
        with open(self.file_path, "w") as f:
            json.dump(data, f, indent=4)

    # --- Facts ---
    def store_fact(self, key, value):
        data = self._load()
        data["facts"][key] = value
        self._save(data)
        return f"Stored fact: {key} = {value}"

    def get_fact(self, key):
        data = self._load()
        return data["facts"].get(key, "No such fact stored")

    def delete_fact(self, key):
        data = self._load()
        if key in data["facts"]:
            del data["facts"][key]
            self._save(data)
            return f"Deleted fact: {key}"
        return "Fact not found"

    # --- Credentials ---
    def store_credential(self, platform, user_id, password):
        data = self._load()
        data["credentials"][platform] = {"user_id": user_id, "password": password}
        self._save(data)
        return f"Stored credentials for {platform}"

    def get_credential(self, platform):
        data = self._load()
        creds = data["credentials"].get(platform)
        if creds:
            return f"ID: {creds['user_id']}, Password: {creds['password']}"
        return "No credentials found for this platform"

    def delete_credential(self, platform):
        data = self._load()
        if platform in data["credentials"]:
            del data["credentials"][platform]
            self._save(data)
            return f"Deleted credentials for {platform}"
        return "Platform not found"

    # --- List all ---
    def list_memory(self):
        data = self._load()
        response = "Facts:\n"
        for k, v in data["facts"].items():
            response += f"- {k}: {v}\n"
        response += "\nCredentials:\n"
        for p, creds in data["credentials"].items():
            response += f"- {p}: ID={creds['user_id']}, Password={creds['password']}\n"
        return response
