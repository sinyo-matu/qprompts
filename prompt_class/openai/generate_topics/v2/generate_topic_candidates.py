from prompt_structure import PromptStructure, Model, ModelConfiguration, ModelParameters, ChatMessage, ChatRole
from typing import list

class GenerateTopicCandidates(PromptStructure):
    def __init__(self):
        super().__init__(
            name='ExamplePrompt',
            description='A prompt that uses context to ground an incoming question',
            authors=['Seth Juarez'],
            model=Model(
                api='chat',
                configuration=ModelConfiguration(
                    type='openai',
                    name='gpt-4o'
                ),
                parameters=ModelParameters(
                    max_tokens=3000,
                )
            ),
            sample={'firstName': 'Seth', 'context': "The Alpine Explorer Tent boasts a detachable divider for privacy,  numerous mesh windows and adjustable vents for ventilation, and  a waterproof design. It even has a built-in gear loft for storing  your outdoor essentials. In short, it's a blend of privacy, comfort,  and convenience, making it your second home in the heart of nature!\n", 'question': 'What can you tell me about your tents?', 'chat_history': {'user': 'What is the price of the {{product}}?', 'assistant': 'The price of the {{product}} is {{price}}'}},
            body={'system': 'You are an AI assistant who helps people find information. As the assistant, \nyou answer questions briefly, succinctly, and in a personable manner using \nmarkdown and even add some personal flair with appropriate emojis.\n\n# Customer\nYou are helping {{firstName}} to find answers to their questions.\nUse their name to address them in your responses.\n\n# Context\nUse the following context to provide a more personalized response to {{firstName}}:\n{{context}}', 'user': '{{question}}'},
        )

    def render_sample(self, price: str, product: str) -> list[ChatMessage]:
        return super().render_sample(price=price, product=product)

    def render_body(self, firstName: str, question: str, context: str) -> list[ChatMessage]:
        return super().render_body(firstName=firstName, question=question, context=context)
