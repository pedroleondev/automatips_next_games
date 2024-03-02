import openai

openai.api_key = 'TOKEN_API'

# Initialize the chat with the first few messages
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Who won the world series in 2020?"},
    {"role": "assistant", "content": "The Los Angeles Dodgers won the World Series in 2020."},
    {"role": "user", "content": "Where was it played?"}
]


def add_message(role, content):
    messages.append({"role": role, "content": content})


def get_response():
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=1,
        max_tokens=200
    )
    return response.choices[0].message['content']


input_message = input('Como posso lhe ajudar?  \n')
add_message("system", input_message)

while input_message.lower() != "fim":
    answer = get_response()
    print("Resposta: ", answer)

    input_message = input('Esperando input: ')
    add_message("system", input_message)
