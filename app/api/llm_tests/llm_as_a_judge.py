from ollama import chat
from ollama import ChatResponse

response: ChatResponse = chat(model='gpt-oss:20b', messages=[
  {
    'role': 'system',
    'content': 'You are a fair judge for AI assistants. You will be provided an instruction,'
               'user message and an AI output to evaluate. Rate the AI output on a scale of'
               '1-5, where 5 is the best outcome. Your output should ONLY be a number from 1-5.',
  },
    {
        'role': 'user',
        'content': 'Instruction: Help users with order cancellations.'
                   'User message: Help me cancel my order.'
                   'AI output: Sure, please provide your order id.',
    },
])
print(response['message']['content'])
# or access fields directly from the response object
print(response.message.content)