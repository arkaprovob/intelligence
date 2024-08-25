import re


def format_readable(text):
    def indent_block(block, level):
        return '\n'.join('  ' * level + line for line in block.split('\n'))

    def format_dict(match):
        content = match.group(1)
        level = len(re.findall(r'^', match.string[:match.start()], re.M)) - 1
        formatted = '{\n'
        for item in re.split(r',\s*(?=\w+:)', content):
            if item.strip():
                formatted += f"  {indent_block(item.strip(), 1)},\n"
        formatted += '}'
        return indent_block(formatted, level)

    # Format dictionaries
    text = re.sub(r'{([^{}]*)}', format_dict, text)

    # Format lists and tuples
    text = re.sub(r'\[(.*?)\]', lambda m: f"[\n  {indent_block(m.group(1), 1)}\n]", text)
    text = re.sub(r'\((.*?)\)', lambda m: f"(\n  {indent_block(m.group(1), 1)}\n)", text)

    # Add newlines after commas in the outer structure
    text = re.sub(r',\s*(?=\w+:)', ',\n', text)

    # Indent the entire text
    text = indent_block(text, 0)

    return text


# Example usage
text = '''{'response_synthesizer:text_qa_template': PromptTemplate(metadata={'prompt_type': <PromptType.CUSTOM: 'custom'>}, template_vars=['context_str', 'query_str', 'tone_name'], kwargs={'tone_name': 'senior support engineer'}, output_parser=None, template_var_mappings=None, function_mappings=None, template='\n        ### Context:\n        {context_str}\n\n        ### Query: {query_str}\n\n        ### Instructions:\n        1. If the context doesn\'t contain enough information to fully answer the query, explicitly state: "The provided information is not sufficient to answer this query."\n        2. If any part of the query cannot be answered based on the context, clearly indicate which parts lack information.\n        3. Write in a {tone_name} tone.\n        4. If you\'re unsure about any aspect of the answer, state your uncertainty clearly.\n\n        ### Answer:\n        '), 'response_synthesizer:refine_template': SelectorPromptTemplate(metadata={'prompt_type': <PromptType.REFINE: 'refine'>}, template_vars=['query_str', 'existing_answer', 'context_msg'], kwargs={}, output_parser=None, template_var_mappings={}, function_mappings={}, default_template=PromptTemplate(metadata={'prompt_type': <PromptType.REFINE: 'refine'>}, template_vars=['query_str', 'existing_answer', 'context_msg'], kwargs={}, output_parser=None, template_var_mappings=None, function_mappings=None, template="The original query is as follows: {query_str}\nWe have provided an existing answer: {existing_answer}\nWe have the opportunity to refine the existing answer (only if needed) with some more context below.\n------------\n{context_msg}\n------------\nGiven the new context, refine the original answer to better answer the query. If the context isn't useful, return the original answer.\nRefined Answer: "), conditionals=[(<function is_chat_model at 0x16d5d4f40>, ChatPromptTemplate(metadata={'prompt_type': <PromptType.CUSTOM: 'custom'>}, template_vars=['context_msg', 'query_str', 'existing_answer'], kwargs={}, output_parser=None, template_var_mappings=None, function_mappings=None, message_templates=[ChatMessage(role=<MessageRole.USER: 'user'>, content="You are an expert Q&A system that strictly operates in two modes when refining existing answers:\n1. **Rewrite** an original answer using the new context.\n2. **Repeat** the original answer if the new context isn't useful.\nNever reference the original answer or context directly in your answer.\nWhen in doubt, just repeat the original answer.\nNew Context: {context_msg}\nQuery: {query_str}\nOriginal Answer: {existing_answer}\nNew Answer: ", additional_kwargs={})]))])}'''

print(format_readable(text))
