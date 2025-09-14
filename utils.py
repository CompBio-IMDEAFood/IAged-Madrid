from datetime import datetime
import pymysql
import os
import json
from virtual_agents import *
from pathlib import Path

def make_dictdb(host, user, passwd, database_name, output_filepath, vars_to_exclude = None):
    conn = pymysql.connect(
        host = host,
        user = user,
        password = passwd,
        database = database_name,
    )

    cursor = conn.cursor()

    # Obtain all tables
    cursor.execute("SHOW TABLES;")
    tablas = [t[0] for t in cursor.fetchall()]

    # Make a dict with the colum_names from each table
    tabla_columnas = {}
    for tabla in tablas:
        cursor.execute(f"SHOW COLUMNS FROM `{tabla}`;")
        columnas = [col[0] for col in cursor.fetchall()]  # col[0] es el nombre de la columna
        tabla_columnas[tabla] = columnas
    
    # To avoid model confusion
    if vars_to_exclude != None:
        if not isinstance(vars_to_exclude, list):
            print("vars_to_exclude argument should be a list of tuples (table_name,column_name)")
        else:
            for table, column in vars_to_exclude:
                tabla_columnas[table].remove(column)
    conn.close()

    # Result
    print(tabla_columnas)
    
    with open(output_filepath, "wt") as db_dict:
        db_dict.write(json.dumps(tabla_columnas, indent=4))
    return json.dumps(tabla_columnas, indent=4)

def count_tokens(string: str, encoding_name: str = "cl100k_base") -> int:
    """Returns the number of tokens in a text string.

    :param string: The text string to count tokens in.
    :param encoding_name: The name of the encoding to use.
    :return: The number of tokens in the text string.
    """
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))

    return num_tokens

def describe_agents(agents: list) -> str:
    agents_prompt = "Your research team is composed of the following members:\n"
    for agent in agents:
        prompt = f'A {agent}, expert in {agent.expertise}. Their goal is {agent.goal}. Their role in the project will be {agent.role}.\n'
        agents_prompt += prompt
    return agents_prompt

class Discussion:
    def __init__(self, title: str, type: str,  goal: str, contributors: list, request: str, deliverable: str, materials: tuple=None, participants_request:str="", participants_request_instructions:str = "", final_request: str = None, moderator: Agent = None, agenda: str = None, scheme: tuple = None) -> None:
        """Initializes the discussion.
        :param type: The title of the discussion.
        :param type: The type of the discussion.
        :param goal: The purpose of the discussion.
        :param contributors: The members of the team that will participate in the discussion
        :param scheme: The scheme of interventions in the discussion in tuple format (rounds:int, participants:list)
        :param agenda: Project context + main points raised from each meeting (in order to give more context for the next one)
        :param request: The final request to get the aim of the discussion.
        """
        self.title = title
        self.type = type
        self.moderator = moderator
        self.goal = goal
        self.contributors = contributors
        self.scheme = scheme
        self.materials = materials
        self.agenda = agenda
        self.request = request
        self.deliverable = deliverable
        self.final_request = final_request
        self.participants_request = f"please provide your {participants_request}. If you do not have anything new or relevant to add, you may say \"pass\". Remember that you can and should (politely) disagree with other team members if you have a different perspective. {participants_request_instructions}"
    

    @property
    def prompt(self) -> str:
        """Returns the prompt for the discussion."""
        base_prompt = (
            f"This is the beginning of a {self.type} "
            f"to {self.goal}.\n"
            f"{self.agenda}"
        )
        if self.type != "individual_meeting":
            f"These are the participants in the {self.type}: {self.contributors}.\n"

        if self.materials:
            description, dict_db = self.materials
            base_prompt += (
                f"\nThe material available for this objective consists of a database of {description}"
                f"The available variables are detailed in a data dictionary, which specifies each table name (key) along with its corresponding list of column names (value). This is the data dictionary: {dict_db}\n"
            )

        if self.scheme: # only for meetings that should follow a scheme of intervention
            rounds, participants = self.scheme
            base_prompt += (
                f"{self.moderator} will convene the meeting."
                f"Throughout the {self.type}, participants will share their perspectives and contributions in the following order: {", ".join(p.title for p in self.contributors)}, over {rounds} rounds.")
            if rounds > 1:    
                base_prompt += (f"In the subsequent rounds, the participants will incorporate their colleagues’ comments to refine and reformulate their ideas. ")
                if scientific_critic.title in participants:
                    base_prompt += (f"At the end of each round, the {scientific_critic.title} will provide feedback on the feasibility of the project and suggestions for improvement. "
                                    f"Then, {self.moderator} summarize the {self.type} in detail for future reference and to have notes for the draft")
            elif self.type=="working session" and self.agenda != "":
                base_prompt += (f"These rounds of discussion should conclude with the division and assignment of tasks, with clarity on which variables, statistical models, and tools will be used. You should make all relevant decisions for the development of the scripts, drawing on the literature and previous discussions, rather than seeking external support. After all team members have shared their perspectives, {self.moderator} will compile a {self.deliverable}")
            else:
                base_prompt += (f"Once all team members have given their input, the {self.moderator} will consolidate all ideas in detail for future reference, to provide notes for the draft, and to serve as guidance for the developers")

        base_prompt += (
                f"\nPlease, {self.moderator}{self.request}" #eval if in beta-assisted chatGPT-api is mandatory include agent-name
            )
        return base_prompt

    @property
    def message(self) -> dict[str, str]:
        """Returns the message for the agent in OpenAI API form."""
        return {
            "role": "system",
            "content": self.prompt,
        }

    @property
    def rounds(self):
        return self.scheme[0]

    @property
    def input_tokens(self) -> int:
        return count_tokens(self.prompt)

import time

def wait_on_run(client, run, thread_id):
    while run.status == "queued" or run.status == "in_progress":
        run = client.beta.threads.runs.retrieve(
            thread_id=thread_id,
            run_id=run.id,
        )
        time.sleep(1.0)
    return run

def save_meeting(
    save_dir: Path, save_name: str, discussion: list[dict[str, str]]
) -> None:
    """Save a meeting discussion to JSON and Markdown files.

    :param save_dir: The directory to save the discussion.
    :param save_name: The name of the discussion file that will be saved.
    :param discussion: The discussion to save.
    """
    # Create the save directory if it does not exist
    save_dir.mkdir(parents=True, exist_ok=True)

    # Save the discussion as JSON
    with open(save_dir / f"{save_name}.json", "w") as f:
        json.dump(discussion, f, indent=4)

    # Save the discussion as Markdown
    with open(save_dir / f"{save_name}.md", "w") as file:
        for turn in discussion:
            file.write(f"## {turn['agent']}\n\n{turn['message']}\n\n")


def summarize_history(client, history):
    """Genera un resumen de la conversación para enviar al asistente."""
    if not history:
        return ""
    thread_sum = client.beta.threads.create()
    # Instrucciones y mensaje de resumen
    summary_prompt = "Summarize the conversation so far:\n"
    instructions = ("Please avoid repeating information. Include any explicit questions or "
                    "instructions that may require intervention from other agents. Ensure that the summary "
                    "contains only relevant information for agents who will continue the conversation later.")
    
    for speaker, msg, _ in history:
    # msg es una lista de objetos MessageContent
        if isinstance(msg, list) and msg and hasattr(msg[0], "text"):
            summary_prompt += f"{speaker}: {msg[0].text.value}\n"
        else:
            # por si msg ya viene como string
            summary_prompt += f"{speaker}: {msg}\n"


    # Enviar al modelo para generar el resumen
    summary_agent = client.beta.assistants.create(  # Asumiendo que esta es la forma de crear un asistente o usar un asistente ya creado.
        name="SummaryAssistant",  # Nombre del asistente que hará el resumen
        instructions=instructions,
        model="gpt-4",  # Modelo que usas, por ejemplo GPT-4
    )
    
    sum_message = client.beta.threads.messages.create(
        thread_id= thread_sum.id,
        role="user",
        content= summary_prompt + instructions,
    )
    
    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread_sum.id,
        assistant_id=summary_agent.id,
        model=summary_agent.model,
        temperature= 0,
    )
    run = wait_on_run(client, run, thread_sum)
    
    sum_response = client.beta.threads.messages.list(thread_id=thread_sum.id)
    
    for message in reversed(sum_response.data):
        if message.role == "assistant" and message.assistant_id == summary_agent.id:
            # opcional: comprobar assistant_id si lo tienes
            summary_response = ""
            for block in message.content:
                if hasattr(block, "text"):
                    summary_response += block.text.value
            break  # ya encontramos el último mensaje de un assistant
    
    return summary_response


default_model = "gpt-4o"

discussions_path = r"c:\Users\Lucia Carrasco\OneDrive - FUNDACION IMDEA-ALIMENTACION\Escritorio\LUCIA\AGED_MADRID\AGENTS4SCIENCE\ChatGPT-api\discussions".replace("\\","/")
# optional parameters to decrease randomness and enhance reproducibility
assistant_params = {
    "memory": {"enabled": False},  # Desactiva memoria si no quieres persistencia
    "temperature": 0 # Disminuir aleatoriedad para favorecer la reproducibilidad
}

def run_discussion(client, discussion: Discussion, moderator: Agent, participants:dict , conversation_log:list = [], thread_id: str=None):
    if thread_id == None:   
        thread = client.beta.threads.create()
        thread_id = thread.id

    assistant_id_to_title = {assistant.id: agent.title for agent, assistant in participants.items()}

    initial_message = discussion.prompt

    user_message = client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=initial_message
    )
    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread_id,
        assistant_id=participants[moderator.title].id,
        model=participants[moderator.title].model,
        temperature=0,
    )
    run = wait_on_run(client, run, thread_id)

    # Última respuesta del moderador

    moderator_response = None
    for _ in range(3):
        response = client.beta.threads.messages.list(thread_id=thread_id)
        
        for message in response.data:
            if message.role == "assistant" and message.assistant_id == participants[moderator.title].id:
                moderator_response = "".join(
                    block.text.value for block in message.content if hasattr(block, "text")
                )
                break 
        time.sleep(5.0) 

    print("=== Mensajes en el hilo ===")
    for i, msg in enumerate(response.data):
        role = msg.role
        aid = getattr(msg, "assistant_id", None)
        print(f"{i}: role={role}, assistant_id={aid}, content={[block.text.value for block in msg.content if hasattr(block, 'text')]}")
    print("===========================")
    conversation_log.append((moderator.title, moderator_response, datetime.now().isoformat()))
    print(f"{moderator.title}: {moderator_response}\n{'-'*50}")
    print(response.data[-1])
    if discussion.scheme:
        for round_num in range(1, discussion.rounds+1):
            for title, assistant in participants.items():
                if title != moderator.title:
                    agent_request = f"{title}, {discussion.participants_request} (round{round_num}/{discussion.rounds})"
                    
                    print(f"\n>>> Context for {title} in round {round_num}:\n{agent_request}\n{'='*70}")

                    user_message = client.beta.threads.messages.create(
                        thread_id=thread_id,
                        role="user",
                        content=agent_request
                    )
                    run = client.beta.threads.runs.create_and_poll(
                        thread_id=thread_id,
                        assistant_id=participants[title].id,
                        model=participants[title].model,
                        temperature=0,
                    )
                    run = wait_on_run(client, run, thread_id)
                    for _ in range(3):
                        response = client.beta.threads.messages.list(thread_id=thread_id)
                        # Última respuesta del moderador

                        assistant_response = None
                        for message in response.data:
                            if message.role == "assistant" and message.assistant_id == participants[title].id:
                                assistant_response = "".join(
                                    block.text.value for block in message.content if hasattr(block, "text")
                                )
                                break
                        time.sleep(5.0) 
                    
                    conversation_log.append((f'{title} round {round_num}/{discussion.rounds}', assistant_response, datetime.now().isoformat()))
                    print(f"{title} round {round_num}/{discussion.rounds}: {assistant_response}\n{'-'*50}")

        #discussion_summary = summarize_history(client, conversation_log)
        moderator_request = f"{moderator.title}, {discussion.final_request}"
        moderator_instructions = f"You should return just the {discussion.deliverable}, without introductory or closing phrases and please respond in a direct manner without emoticons. Include  relevant comments and only use a list if necessary, and if so, use a simple list."
        final_message = moderator_request + moderator_instructions
        print(final_message)

        user_message = client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=final_message
        )
        run = client.beta.threads.runs.create_and_poll(
            thread_id=thread_id,
            assistant_id=participants[moderator.title].id,
            model=participants[moderator.title].model,
            temperature=0,
        )
        
        run = wait_on_run(client, run, thread_id)
        
        # volver a pedir mensajes ya con el run completado
        for _ in range(5):
            response = client.beta.threads.messages.list(thread_id=thread_id)
            # Última respuesta del moderador
            moderator_response = None
            for message in response.data:
                if message.role == "assistant" and message.assistant_id == participants[moderator.title].id:
                    moderator_response = "".join(
                        block.text.value for block in message.content if hasattr(block, "text")
                    )
                    break
            time.sleep(10.0) 
        print("=== Mensajes en el hilo ===")
        for i, msg in enumerate(response.data):
            role = msg.role
            aid = getattr(msg, "assistant_id", None)
            print(f"{i}: role={role}, assistant_id={aid}, content={[block.text.value for block in msg.content if hasattr(block, 'text')]}")
        print("===========================")
        conversation_log.append((moderator.title, moderator_response, datetime.now().isoformat()))
        print(f"{moderator.title}: {moderator_response}\n{'-'*50}")

    discussion_deliverable = moderator_response
    return discussion_deliverable, conversation_log, thread_id

class Code_development:
    def __init__(self, title: str, type: str,  goal: str, contributors: list, request: str, deliverable: list, materials: tuple=None, participants_request:str="", participants_request_instructions:str = "", final_request: str = None, moderator: Agent = None, agenda: str = None, scheme: tuple = None) -> None:
        """Initializes the discussion.
        :param type: The title of the discussion.
        :param type: The type of the discussion.
        :param goal: The purpose of the discussion.
        :param contributors: The members of the team that will participate in the discussion
        :param scheme: The scheme of interventions in the discussion in tuple format (rounds:int, participants:list)
        :param agenda: Project context + main points raised from each meeting (in order to give more context for the next one)
        :param request: The final request to get the aim of the discussion.
        """
        self.title = title
        self.type = type
        self.moderator = moderator
        self.goal = goal
        self.agenda = agenda
        self.request = request
        self.deliverable = deliverable
        self.final_request = final_request
        self.participants_request = participants_request
        self.contributors = contributors
        self.materials = materials
        self.participants_request_instructions = participants_request_instructions
    

    @property
    def prompt(self) -> str:
        """Returns the prompt for the discussion."""
        base_prompt = (
            f"This is the beginning of the code-development phase of the {self.type}"
            f"to {self.goal}.\n"
            f"{self.agenda}"
        )
        if self.type != "individual_meeting":
            f"These are the participants in the {self.type}: {self.contributors}.\n"

        if self.materials:
            description, dict_db = self.materials
            base_prompt += (
                f"The material available for this objective consists of a database of {description}"
                f"The available variables are detailed in a data dictionary, which specifies each table name (key) along with its corresponding list of column names (value). This is the data dictionary: {dict_db}\n"
            )

        
        rounds = len(self.deliverable)
        
        base_prompt += (
            f"{self.moderator} will convene the meeting."
            f"Throughout the {self.type}, the developers will develop the code individually for each scriptin each round.\n"
            f"Then, {self.moderator} summarize the {self.type}in detail to have notes for the draft.\n"
            f"Remind that the resultant code should generate output tables and plots."
            f"The scripts should be structured following a clear directory hierarchy to ensure organization and reproducibility. At a minimum, the project should include the following folders: (a) raw_data/, to store the original input files (e.g., CSVs, databases); (b) scripts/, to store all processing and analysis scripts; (c) output/, to store processed data, results, and figures; (d) docs/, to store documentation, notes, or metadata; (e) logs/, to capture execution logs, if applicable; Make sure the scripts automatically create these folders (if they do not exist) before writing files. No files should be generated outside of these directories.")
 
        
        
        base_prompt += (
                f"\nPlease, {self.moderator} {self.request}" #eval if in beta-assisted chatGPT-api is mandatory include agent-name
            )
        return base_prompt

    @property
    def message(self) -> dict[str, str]:
        """Returns the message for the agent in OpenAI API form."""
        return {
            "role": "system",
            "content": self.prompt,
        }

    @property
    def input_tokens(self) -> int:
        return count_tokens(self.prompt)
    

def run_code_development(client, discussion: Discussion, moderator: Agent, participants:dict , conversation_log:list = [], thread_id: str=None):
    if thread_id == None:   
        thread = client.beta.threads.create()
        thread_id = thread.id

    initial_message = discussion.prompt

    user_message = client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=initial_message
    )
    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread_id,
        assistant_id=participants[moderator.title].id,
        model=participants[moderator.title].model,
        temperature=0,
    )
    time.sleep(2.0)
    run = wait_on_run(client, run, thread_id)

    # Última respuesta del moderador

    moderator_response = None
    for _ in range(3):
        response = client.beta.threads.messages.list(thread_id=thread_id)
        
        for message in response.data:
            if message.role == "assistant" and message.assistant_id == participants[moderator.title].id:
                moderator_response = "".join(
                    block.text.value for block in message.content if hasattr(block, "text")
                )
                break 
        time.sleep(10.0) 

    conversation_log.append((moderator.title, moderator_response, datetime.now().isoformat()))
    print(f"{moderator.title}: {moderator_response}\n{'-'*50}")
    print(response.data[-1])
    
    for i, deli in enumerate(discussion.deliverable):
        agent_request = f"{deli[1]}{discussion.participants_request}{deli[0]}{discussion.participants_request_instructions}"
        print(f"\n>>> Context for {deli[0]}:\n{agent_request}\n{'='*70}")

        user_message = client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=agent_request
        )
        run = client.beta.threads.runs.create_and_poll(
            thread_id=thread_id,
            model=participants[deli[1]].model,
            assistant_id=participants[deli[1]].id,
            temperature=0,
        )
        run = wait_on_run(client, run, thread_id)
        if i == 0:
            last_assistant_response = None
        for _ in range(3):
            response = client.beta.threads.messages.list(thread_id=thread_id)
            
            # Última respuesta del moderador
            assistant_response = None
            for message in response.data:
                if message.role == "assistant" and message.assistant_id == participants[deli[1]].id and response!=last_assistant_response:
                    assistant_response = "".join(
                        block.text.value for block in message.content if hasattr(block, "text")
                    )
                    break
            time.sleep(10.0) 
            last_assistant_response = response
        
        conversation_log.append((f'{deli[0]}', assistant_response, datetime.now().isoformat()))
        print(f"{deli[0]}: {assistant_response}\n{'-'*50}")

    #discussion_summary = summarize_history(client, conversation_log)
    moderator_request = f"{moderator.title}, {discussion.final_request}"
    moderator_instructions = f"You should return just the methodology details to consider it in manuscript drafting, without introductory or closing phrases and please respond in a direct manner without emoticons. Include  relevant comments and only use a list if necessary, and if so, use a simple list."
    final_message = moderator_request + moderator_instructions
    print(final_message)

    user_message = client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=final_message
    )
    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread_id,
        assistant_id=participants[moderator.title].id,
        model=participants[moderator.title].model,
        temperature=0,
    )
    
    run = wait_on_run(client, run, thread_id)
    
    # volver a pedir mensajes ya con el run completado
    for _ in range(5):
        response = client.beta.threads.messages.list(thread_id=thread_id)
        # Última respuesta del moderador
        moderator_response = None
        for message in response.data:
            if message.role == "assistant" and message.assistant_id == participants[moderator.title].id:
                moderator_response = "".join(
                    block.text.value for block in message.content if hasattr(block, "text")
                )
                break
        time.sleep(10.0) 

    conversation_log.append((moderator.title, moderator_response, datetime.now().isoformat()))
    print(f"{moderator.title}: {moderator_response}\n{'-'*50}")
    ws_summary = moderator_response
    return ws_summary, conversation_log, thread_id


def run_paper_drafting(client, discussion: Discussion, moderator: Agent, sections: dict, participants: dict, thread_id: str=None, conversation_log: list=[]):
    if thread_id == None:   
        thread = client.beta.threads.create()
        thread_id = thread.id

    initial_message = discussion.prompt

    user_message = client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=initial_message
    )
    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread_id,
        assistant_id=participants[moderator.title].id,
        model=participants[moderator.title].model,
        temperature=0,
    )
    time.sleep(10.0)
    run = wait_on_run(client, run, thread_id)

    # Última respuesta del moderador

    moderator_response = None
    for _ in range(3):
        response = client.beta.threads.messages.list(thread_id=thread_id)
        
        for message in response.data:
            if message.role == "assistant" and message.assistant_id == participants[moderator.title].id:
                moderator_response = "".join(
                    block.text.value for block in message.content if hasattr(block, "text")
                )
                break 
        time.sleep(10.0) 

    conversation_log.append((moderator.title, moderator_response, datetime.now().isoformat()))
    print(f"{moderator.title}: {moderator_response}\n{'-'*50}")
    print(response.data[-1])
    
    for i, section in enumerate(sections.keys()):
        agent_request = f"Please, continue with section {section}, following this instructions: {sections[section]}"
        print(f"\n>>> Context for {section} drafting: {agent_request}\n{'='*70}")

        user_message = client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=agent_request
        )
        run = client.beta.threads.runs.create_and_poll(
            thread_id=thread_id,
            model=participants[moderator.title].model,
            assistant_id=participants[moderator.title].id,
            temperature=0,
        )
        run = wait_on_run(client, run, thread_id)
        if i == 0:
            last_assistant_response = None
        for _ in range(3):
            response = client.beta.threads.messages.list(thread_id=thread_id)
            # Última respuesta del moderador

            assistant_response = None
            for message in response.data:
                if message.role == "assistant" and message.assistant_id == participants[moderator.title].id:
                    assistant_response = "".join(
                        block.text.value for block in message.content if hasattr(block, "text")
                    )
                    break
            time.sleep(10.0) 
            last_assistant_response = response
        
        conversation_log.append((f'({section}', assistant_response, datetime.now().isoformat()))
        print(f"{section}: {assistant_response}\n{'-'*50}")
    
    return conversation_log

