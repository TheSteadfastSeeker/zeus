import asyncio
import time

from tools.llm_configuration import OllamaLLMConfiguration as Configuration

configuration = Configuration()
llm = configuration.get_llm(temperature=0)

async def a_simple_calculator_llm() -> list[str]:
    start = time.time()
    result1 = llm.ainvoke("Is there life in Goldilocks zone of black hole.")
    result2 = llm.ainvoke("write a song about never giving up.")
    result3 = llm.ainvoke("describe the deepest part of the ocean.")
    end = time.time()
    print(f" reached a_here in... {end-start}") # reached a_here in... 5.0067901611328125e-06
    return [(await result1).content, (await result2).content, (await result3).content]

def simple_calculator_llm() -> list[str]:
    start = time.time()
    result1 = llm.invoke("Is there life in Goldilocks zone of black hole.")
    result2 = llm.invoke("write a song about never giving up.")
    result3 = llm.invoke("describe the deepest part of the ocean.")
    end = time.time()
    print(f" reached here in... {end-start}") #  reached here in... 77.1896984577179
    return [result1.content, result2.content, result3.content]

async def main():
    result5 = await a_simple_calculator_llm()
    print(f"long awaited results.. {result5}")

asyncio.run(main())
result4 = simple_calculator_llm()
print(f"not awaited results.. {result4}")
