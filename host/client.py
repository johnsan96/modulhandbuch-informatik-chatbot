import asyncio
import os
from typing import Optional
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from google import genai
from google.genai import types
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv() 

async def main():
    print("Starte MCP-Client...")
    server_params = StdioServerParameters(
        command="/var/www/html/jdoctolero/modulhandbuch-informatik-chatbot/mcp-server/.venv/bin/python",
        args=["/var/www/html/jdoctolero/modulhandbuch-informatik-chatbot/mcp-server/main.py"],
        env=None
    )
        
    # Session aufbauen
    async with stdio_client(server_params) as (reader, writer):
        async with ClientSession(reader, writer) as session:
            await session.initialize()
            print("Verbunden mit MCP-Server.")

            response = await session.list_tools()
            tools = response.tools
            print("\n🛠 Verfügbare Tools auf dem MCP-Server:")
            for tool in tools:
                print(f"\n🔹 Name: {tool.name}")
                print(f"   Beschreibung: {tool.description}")
                print(f"   InputSchema: {tool.inputSchema}")

            function_declarations = []
            for tool in tools:
                function_declarations.append({
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.inputSchema
                })

            tools = types.Tool(function_declarations=function_declarations)
            config = types.GenerateContentConfig(tools=[tools])

            #result = await session.call_tool("get_modul_details", {"titel_suche": "Programmieren"})
            #print(f"📚 Tool-Antwort: {result}")

            # Google Gemini Setup
            client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

            #user_prompt = "Erkläre wie AI funktioniert"
            #response = client.models.generate_content(
            #        model="gemini-2.0-flash",
            #         contents="Erkläre wie AI funktioniert ganz kurz in 1 satz"
            #        )
            #print(f"🤖 Gemini sagt: {response.text}")

            while True:
                user_input = input("\nQuery (exit zum Beenden): ")
                if user_input.strip().lower() == "exit":
                    break

                gemini_response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=user_input,
                    config=config
                )

                handled = False

                for part in gemini_response.candidates[0].content.parts:
                    if hasattr(part, "function_call") and part.function_call is not None:
                         fc = part.function_call
                         print(f"➡ Gemini möchte Tool {fc.name} mit {fc.args}")
                         result = await session.call_tool(fc.name, fc.args)
                         #print(f"✅ Ergebnis von {fc.name}:\n{result}")
                         tool_output = result.content[0].text

                         response = client.models.generate_content(
                                 model="gemini-2.5-flash",
                                 contents=f"""Hier sind die rohen Ergebnisse aus der Datenbank:
                                 {tool_output}
                                 Formuliere daraus bitte eine freundliche Antwort für den Nutzer, die erklärt, welche Module gefunden wurden."""
                                 )
                         print(f"🤖 Bot: {response.text}")

                         handled = True
                    elif hasattr(part, "text"):
                         print(f"💬 Bot: {part.text}")
                         handled = True
                if not handled:
                     print("⚠️ Keine Antwort vom Bot gefunden.")
    

if __name__ == "__main__":
    asyncio.run(main())
