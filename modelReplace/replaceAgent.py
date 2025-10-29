import os
import re
import shutil

def replaceWithCustomModel(repo_path):
    file_exts = ('.py',)
    backup = False
    HOSTED_ENDPOINT = "os.getenv('ENDPOINT')"
    API_KEY = "os.getenv('API_KEY')"

    INLINE_MODEL_DEF = '''import requests,os
    from dotenv import load_dotenv
    load_dotenv()

    class MyHostedModel:
        def __init__(self, endpoint, api_key=None, timeout=60):
            self.endpoint = endpoint
            self.api_key = api_key
            self.timeout = timeout

        def _call_api(self, prompt, **kwargs):
            headers = {{}}
            if self.api_key:
                headers["Authorization"] = f"Bearer {{self.api_key}}"
            payload = {{"prompt": prompt}}
            payload.update(kwargs)
            resp = requests.post(self.endpoint, headers=headers, json=payload, timeout=self.timeout)
            try:
                data = resp.json()
                return data
            except Exception:
                return resp

        def predict(self, prompt, **kwargs):
            return self._call_api(prompt, **kwargs)

        def invoke(self, prompt, **kwargs):
            return self._call_api(prompt, **kwargs)

        def generate(self, prompt, **kwargs):
            return self._call_api(prompt, **kwargs)
        
        def generate_content(self, prompt, **kwargs):
            return self._call_api(prompt, **kwargs)

        def __call__(self, prompt, **kwargs):
            return self._call_api(prompt, **kwargs)

    {var_name} = MyHostedModel(endpoint={endpoint}, api_key={api_key})
    '''


    # === REGEXES ===
    api_key_patterns = [
        r".*api[_ ]?key.*=",
        r".*os\.getenv\(.*api.*\)",
        r".*os\.environ\[.*api.*\]",
        r".*set_api_key\(.*\)",
        r".*configure\(.*api.*\)",
        r".*openai\.api_key.*",
    ]

    # Match only model initialization (not .predict etc.)
    # Exclude embeddings, tokenizers, and client definitions.
    model_patterns = [
        r"^\s*(\w+)\s*=\s*.*\b("
        r"OpenAI|ChatOpenAI|GenerativeModel|Gemini|Anthropic|Claude|HuggingFace|"
        r"Llama|Ollama|AutoModel|Transformers|GPT|Model"
        r")\b\s*\(",
    ]

    exclude_patterns = [
        r"embedding", r"tokenizer", r"client", r"pipeline", r"sentencepiece"
    ]

    api_key_regex = re.compile("|".join(api_key_patterns), re.IGNORECASE)
    model_regex = re.compile("|".join(model_patterns), re.IGNORECASE)
    exclude_regex = re.compile("|".join(exclude_patterns), re.IGNORECASE)

    for root, _, files in os.walk(repo_path):
        for file in files:
            if not file.endswith(file_exts):
                continue

            path = os.path.join(root, file)
            with open(path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            new_lines = []
            model_found = False
            model_var_name = None

            for line in lines:
                # Skip any API key lines
                if api_key_regex.search(line):
                    continue

                if exclude_regex.search(line):
                    new_lines.append(line)
                    continue

                model_match = model_regex.search(line)
                if model_match:
                    model_var_name = model_match.group(1)
                    model_found = True

                    new_lines.append(
                        INLINE_MODEL_DEF.format(
                            var_name=model_var_name,
                            endpoint=HOSTED_ENDPOINT,
                            api_key=API_KEY
                        )
                    )
                    continue

                new_lines.append(line)

            if model_found:
                new_content = "".join(new_lines)
                if backup:
                    shutil.copy(path, path + ".bak")

                with open(path, "w", encoding="utf-8") as f:
                    f.write(new_content)

                print(f"✅ Replaced model in: {path}")

    print("🎯 Replacement complete.")


# repo_path = "./agentDirectory/MTRagEval"
# replaceWithCustomModel(repo_path)