"""
AstraGPT CLI Chat Client (Advanced OOP + Type-Safe Version)
Author: InfernalAtom683
License: MIT

Description:
    An advanced command-line chat interface for OpenAI models using dynamic key 
    generation and colored output. Designed for extensibility, security, and 
    open-source compliance. Every variable and method is explicitly typed.
"""

import openai
import datetime
import hashlib
from time import sleep
from os import system, name
from random import choice
from typing import List, Union, Optional, Literal
from colorama import init, Fore

# Initialize terminal color settings for cross-platform compatibility
init(autoreset=True)


class KeyGenerator:
    """
    Handles dynamic generation and validation of secure hashed keys.
    """

    @staticmethod
    def generate_keys(mode: Literal["normal", "shared"]) -> Union[List[str], str]:
        today: datetime.date = datetime.date.today()
        year: int = today.year
        month: int = today.month
        day: int = today.day

        # Obfuscated cryptographic seed
        raw_seed: int = (month ** 2) * (year ** day) * (2 ** day)
        _hashed_seed: str = hashlib.sha256(str(raw_seed).encode()).hexdigest()

        # Multiple intermediate key formulas
        key0_raw: int = 2 * year + 7 * (month ** round(day / 2.5)) + day ** (
            round(day / 2) + round(day % 3 + 0.5 ** (day ** 0.6))
        )
        key1_raw: int = round((key0_raw + 1 - month) ** 0.8)
        key2_raw: int = round(key0_raw * (month + year - day * 2) + key1_raw ** 0.5 - 2 ** month)
        key3_raw: int = round(
            ((key1_raw + key2_raw) / 2 + (key1_raw / key0_raw) ** (day + (month % 3) % 2)) * month ** 3.14
        )

        # Final hashed keys
        key0: str = hashlib.sha256(str(key0_raw).encode()).hexdigest()
        key1: str = hashlib.sha256(str(key1_raw).encode()).hexdigest()
        key2: str = hashlib.sha256(str(key2_raw).encode()).hexdigest()
        key3: str = hashlib.sha256(str(key3_raw).encode()).hexdigest()

        keys: List[str] = [key0, key1, key2, key3]

        if mode == "normal":
            return keys
        elif mode == "shared":
            shared_key: str = hashlib.sha256((key0 + key1).encode()).hexdigest()
            return shared_key
        else:
            raise ValueError("Unsupported key mode.")


class AstraGPTClient:
    """
    Encapsulates interaction logic with the OpenAI chat model using a conversation history.
    """

    def __init__(self, api_key: str, base_url: str, model: str = "gpt-3.5-turbo") -> None:
        self.api_key: str = api_key
        self.base_url: str = base_url
        self.model: str = model
        self.prompt: str = (
            "You are an AI named 'Astra GPT'. Your author is InfernalAtom683. "
            "You speak English, Chinese, Korean and Arabic."
        )
        self.history: List[dict[str, str]] = [{"role": "system", "content": self.prompt}]
        self.client: openai.OpenAI = openai.OpenAI(api_key=self.api_key, base_url=self.base_url)
        openai.default_headers = {"x-foo": "true"}

    def chat(self, user_input: str, model_override: Optional[str] = None) -> None:
        """
        Sends user input to OpenAI API and prints streaming response.
        """
        user_message: dict[str, str] = {"role": "user", "content": user_input}
        self.history.append(user_message)

        selected_model: str = model_override if model_override else self.model
        response = self.client.chat.completions.create(
            model=selected_model,
            messages=self.history,
            temperature=1.0,
            stream=True
        )

        print(Fore.BLUE + "AstraGPT > ", end="")
        collected_chunks: List[str] = []

        for chunk in response:
            chunk_data: Optional[str] = chunk.choices[0].delta.content
            display_chunk: str = chunk_data if chunk_data is not None else ""
            print(display_chunk, end="", flush=True)
            collected_chunks.append(display_chunk)

        print()  # newline
        full_reply: str = ''.join(collected_chunks)
        assistant_message: dict[str, str] = {"role": "assistant", "content": full_reply}
        self.history.append(assistant_message)


class CLIInterface:
    """
    Provides CLI-based interaction, including input, output, and system operations.
    """

    @staticmethod
    def clear_screen() -> None:
        """
        Clears the terminal based on the operating system.
        """
        os_name: str = name
        command: str = "cls" if os_name in ("nt", "dos") else "clear"
        system(command)

    @staticmethod
    def prompt_for_key() -> str:
        """
        Prompts the user for a key and validates it against generated keys.
        Returns the model type to use.
        """
        while True:
            user_key: str = input("Key: ")
            normal_keys: List[str] = KeyGenerator.generate_keys("normal")
            shared_key: str = KeyGenerator.generate_keys("shared")

            if user_key in normal_keys:
                return "gpt-3.5-turbo"
            elif user_key == shared_key:
                print("Shared key accepted. Switching to GPT-4o Mini.")
                return "gpt-4o-mini"
            else:
                print(Fore.RED + "Incorrect Key!")


def main() -> None:
    """
    Entry point for the CLI chatbot.
    """
    # Replace this placeholder with a secure method like environment variable or file config
    placeholder_keys: List[str] = ["sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"]
    selected_api_key: str = choice(placeholder_keys)
    base_url: str = "https://free.v36.cm/v1/"

    model_type: str = CLIInterface.prompt_for_key()
    chat_client: AstraGPTClient = AstraGPTClient(api_key=selected_api_key, base_url=base_url, model=model_type)

    print("Connecting to server...")
    sleep(2)
    CLIInterface.clear_screen()

    while True:
        try:
            user_input: str = input(Fore.YELLOW + "You > " + Fore.WHITE).strip()
            if user_input.lower() == "/quit":
                print("bye!")
                break
            elif user_input == "":
                continue
            else:
                chat_client.chat(user_input)
        except Exception as e:
            error_message: str = str(e)
            print(Fore.RED + f"Server Error (Code: 0x00000000): {error_message}")


if __name__ == "__main__":
    main()
