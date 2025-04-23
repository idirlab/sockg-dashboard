import streamlit as st
from components.navigation_bar import navigation_bar
from SPARQLWrapper import SPARQLWrapper, CSV
from code_editor import code_editor
import pandas as pd
from io import StringIO
import os

# Text2Cypher imports
from text2sparql.fetch_context import fetch_ontology_context
from text2sparql.prompt_template import generate_prompt, extract_sparql_query
from text2sparql.models import LLM_MODEL


SPARQL_ENDPOINT = os.getenv('SPARQL_ENDPOINT')
state = st.session_state

# --------------------------- Page Setup --------------------------- #
st.set_page_config(layout="wide", page_title="Text2Sparql View", page_icon=":keyboard:")
navigation_bar()
st.markdown("<h1 style='text-align: center; color: #4CAF50;'>Text To Sparql</h1>", unsafe_allow_html=True)
st.subheader("Describe your query in natural language")


# --------------------------- Session State Init --------------------------- #
def init_state(key, value):
    if key not in state:
        state[key] = value

for k, v in {
    'generated_sparql_query': None,
    'query_result': None,
    'user_input': "",
    'generating': False,
    'relevant_classes': None,

}.items():
    init_state(k, v)

# Take the user input and generate a SPARQL query call back
def generate_callback():
    state['relevant_classes'] = None
    state['generated_sparql_query'] = None
    state['query_result'] = None
    state['generating'] = True

# --------------------------- Check query parameter --------------------------- #
# st.write(st.query_params)
if 'q' in st.query_params:
    state['user_input'] = st.query_params['q']
    st.query_params.clear()
    generate_callback()

# --------------------------- Core Logic --------------------------- #    
def generate_sparql(user_question):
    model = LLM_MODEL(os.getenv('LLM_MODEL'))
    onto_context = fetch_ontology_context(user_question)
    # Convert the ontology context to a string
    onto_text = [c['summary'] for c in onto_context]
    onto_context_str = "\n\n".join(onto_text)

    prompt = generate_prompt(user_question, "", onto_context_str)
    response = model.generate(prompt)
    generated_sparql = extract_sparql_query(response)

    # make a dictionary to store the generated query and intermediate steps
    response = {
        "relevant_classes": onto_context,
        "generated_query": generated_sparql,
    }
    return response

def execute_sparql_query(query):
    sparql_client = SPARQLWrapper(SPARQL_ENDPOINT)
    sparql_client.setReturnFormat(CSV)
    sparql_client.setQuery(query)
    response = sparql_client.queryAndConvert()

    # Read the CSV using pandas read_csv
    csv_data = response.decode('utf-8')
    csv_io = StringIO(csv_data)
    response = pd.read_csv(csv_io)
    return response

# --------------------------- UI: Input --------------------------- #
state['user_input'] = st.text_input(
    label="Natural Language Query",
    value=state.user_input,
    key='user_input_textbox',
    placeholder="e.g. Return a random experimental unit located in Texas",
    label_visibility='collapsed'
)
st.button("🔄 Generate", type="primary", on_click=generate_callback)

# --------------------------- SPARQL Generation --------------------------- #
if state['generating']:
    with st.spinner("🔧 Generating SPARQL..."):
        try:
            res = generate_sparql(state.user_input)
            state['generated_sparql_query'] = res['generated_query']
            state['relevant_classes'] = res['relevant_classes']
        except Exception as e:
            st.error(f"❌ Error generating query: {e}")
        finally:
            state['generating'] = False

# --------------------------- UI: Code Editor --------------------------- #
if state['generated_sparql_query']:
    # Hide the generated SPARQL query by default
    with st.expander("Show hidden step", expanded=False):
        st.markdown("##### 1. Fetch Relevant Ontology")
        st.markdown("This step fetch a subset of the ontology that is relevant to the user query using embedding. The relevant classes that seem to be related to the user query are shown below.")
        relevant_classes = state['relevant_classes']
        
        # Limit number of columns per row
        max_cols_per_row = 4

        # Chunk the relevant_classes list
        for i in range(0, len(relevant_classes), max_cols_per_row):
            chunk = relevant_classes[i:i + max_cols_per_row]
            cols = st.columns(len(chunk))  # Create columns only for this chunk
            for col, cls in zip(cols, chunk):
                with col:
                    with st.popover(label=cls['name']):
                        st.text(cls['summary'])

        st.markdown("##### 2. Generated SPARQL Query")
        st.markdown("Using the above ontology context, llm is prompted to generate a SPARQL query. The generated query is shown below.")
        response = code_editor(
            code=state['generated_sparql_query'],
            lang='sparql',
            theme='github-light',
            height=200,
            key='sparql_code_editor',
            allow_reset=True,
            shortcuts="vscode",
            buttons=[{
                "name": "Run",
                "feather": "Play",
                "primary": True,
                "hasText": True,
                "showWithIcon": True,
                "alwaysOn": True,
                "commands": ["submit"],
                "style": {"bottom": "0.44rem", "right": "0.4rem"}
            }]
        )
        st.info("The generated query may be incorrect — feel free to edit it in the code editor above and click Run to execute it.")
        if response and response.get("type") == "submit":
            final_query = response.get("text", "")
            state['generated_sparql_query'] = final_query
            try:
                result = execute_sparql_query(final_query)
                state['query_result'] = result
            except Exception as e:
                st.error(f"❌ Error executing query: {e}")
                result = None


    # Rerun query result if the button is clicked
    if state['query_result'] is None:
        state['query_result'] = execute_sparql_query(state['generated_sparql_query'])
    st.markdown("### Query Result")
    st.dataframe(
        data=state['query_result'],
        use_container_width=True,
        hide_index=True,
    )