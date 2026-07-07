"""Wrapper para API Speack e 69ms de deobfuscacao."""
import os
import requests

API_URL = "https://api-speack.onrender.com/speack/api/v1/deobf"
API_69MS = "https://web-production-99b02d.up.railway.app/deobfuscate"


def _clean_output(text: str) -> str:
    lines = text.splitlines()
    if lines and "Speack" in lines[0]:
        lines[0] = "-- Deobf by Speack | https://discord.gg/SxfqCrd952"
    return "\n".join(lines)


def deobfuscate(code: str, mode: str = "moonsecv3") -> str:
    import tempfile
    with tempfile.NamedTemporaryFile(mode="w", suffix=".lua", delete=False) as f:
        f.write(code)
        tmp_path = f.name

    try:
        with open(tmp_path, "rb") as f:
            response = requests.post(
                API_URL,
                files={"file": f},
                timeout=120
            )

        if response.status_code == 200:
            return _clean_output(response.text)
        else:
            return f"Erro da API: HTTP {response.status_code} - {response.text}"
    except requests.RequestException as e:
        return f"Erro de conexao: {e}"
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


def deobfuscate_from_url(url: str, mode: str = "moonsecv3") -> str:
    try:
        response = requests.post(
            API_URL,
            data={"url": url},
            timeout=120
        )

        if response.status_code == 200:
            return _clean_output(response.text)
        else:
            return f"Erro da API: HTTP {response.status_code} - {response.text}"
    except requests.RequestException as e:
        return f"Erro de conexao: {e}"


def deobfuscate_69ms(code: str) -> str:
    try:
        response = requests.post(
            API_69MS,
            json={"code": code},
            timeout=120
        )

        data = response.json()
        if response.status_code == 200 and data.get("success"):
            return _clean_output(data["result"])
        else:
            error = data.get("error", "unknown error")
            return f"Erro da API: HTTP {response.status_code} - {error}"
    except requests.RequestException as e:
        return f"Erro de conexao: {e}"
    except ValueError:
        return f"Erro da API: HTTP {response.status_code} - {response.text[:200]}"


def deobfuscate_69ms_from_url(url: str) -> str:
    try:
        r = requests.get(url, timeout=30)
        if r.status_code != 200:
            return f"Erro ao baixar URL: HTTP {r.status_code}"
        code = r.text

        response = requests.post(
            API_69MS,
            json={"code": code},
            timeout=120
        )

        data = response.json()
        if response.status_code == 200 and data.get("success"):
            return _clean_output(data["result"])
        else:
            error = data.get("error", "unknown error")
            return f"Erro da API: HTTP {response.status_code} - {error}"
    except requests.RequestException as e:
        return f"Erro de conexao: {e}"
    except ValueError:
        return f"Erro da API: HTTP {response.status_code} - {response.text[:200]}"
