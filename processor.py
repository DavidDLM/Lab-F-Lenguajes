import copy
import pydot
from machine import *
from collections import OrderedDict
import prettytable as pt
from fpdf import FPDF

HEADER = """
from processor import *
from fpdf import FPDF

processor = Processor('YAPar/' + 'yap1' + '.yalp')
processor.compiler()
"""
PDFCLASS = """
class PDF(FPDF):
    def header(this):
        this.set_font("Arial", "B", 12)
        this.cell(0, 10, "SLR Parser Report", ln=True)

    def footer(this):
        this.set_y(-15)
        this.set_font("Arial", "I", 8)
        this.cell(0, 10, f"Page {this.page_no()}", 0, 0, "C")

    def chapter_title(this, title):
        this.set_font("Arial", "B", 12)
        this.ln(10)
        this.cell(0, 10, title, ln=True)

    def chapter_body(this, counter, stack, symbols, dataCopy, actionList, errorList):
        this.set_font("Arial", "", 12)
        this.cell(0, 10, f"Iteration {counter}:", ln=True)
        this.cell(0, 10, f"Stack: {str(stack)}", ln=True)
        this.cell(0, 10, f"Symbols: {str(symbols)}", ln=True)
        this.cell(0, 10, f"Input: {str(dataCopy)}", ln=True)
        this.ln(10)
        this.cell(0, 10, "Actions:", ln=True)
        for action in actionList:
            this.cell(0, 10, action, ln=True)
        this.ln(10)
        if errorList:
            this.cell(0, 10, "Errors:", ln=True)
            for error in errorList:
                this.cell(0, 10, error, ln=True)
        this.ln(10)
"""

BODY = r"""
def main():
    filename = 'YAParFiles/' + 'input1' + '.txt'
    with open(filename, 'r') as file:
        data = file.read().split()
    data.append('$')
    parse(data)

def parse(data):
    stack = []
    symbols = []
    errorList = []
    dataCopy = data.copy()
    actionTable = processor.actionTable
    gotoTable = processor.goToTable
    grammar = processor.grammar
    stack.append(next(iter(actionTable)))
    production_numbers = enumerateGrammar(grammar.productions)
    going = True
    counter = 0

    # Create a PDF instance
    pdf = PDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    # Add a new page
    pdf.add_page()
    # Set font and size for the chapter title
    pdf.set_font("Arial", "B", 16)
    actionList = []  # Initialize the actionList

    while going:
        counter += 1
        lastStack = stack[-1]
        firstData = data[0]
        if actionTable.get(lastStack, {}).get(firstData) == 'acc':
            going = False
            break
        elif actionTable.get(lastStack, {}).get(firstData, '\nerror')[0] == 's':
            symbols.append(firstData)
            stack.append(int(actionTable[lastStack][firstData][1:]))
            data.pop(0)
            action = 'Shift'
            actionList.append(action)  # Add the action to actionList
        elif actionTable.get(lastStack, {}).get(firstData, '\nerror')[0] == 'r':
            prodNumber = int(actionTable[lastStack][firstData][1:])
            for production, number in production_numbers.items():
                if number == prodNumber:
                    break
            else:
                errorList.append("Error: Invalid production number '" + number +
                                 "'")
                break
            prodList = production.split()
            if len(prodList) > len(stack):
                errorList.append(
                    "Error: Reduction 'r" + prodNumber + "' cannot be performed due to insufficient symbols in the stack")
                break
            for _ in range(len(prodList)):
                stack.pop()
            header = None
            for key, value in grammar.productions.items():
                if production in value:
                    header = key
                    break
            else:
                errorList.append(
                    "Error: Production header '" + header + "' not found")
                break
            prodList = production.split()
            symbolList = symbols[:]
            for i in range(len(symbolList)):
                if symbolList[i:i + len(prodList)] == prodList:
                    symbolList[i:i + len(prodList)] = [header]
            symbols = symbolList
            try:
                stack.append(gotoTable[stack[-1]][header])
            except KeyError:
                errorList.append("Error: Invalid input '(" + str(lastStack) +
                                 "," + firstData + ")' in goto table")
                break
            action = f"Reduce using {header} -> {production}"
            actionList.append(action)  # Add the action to actionList

        # Add the chapter title to the PDF
        pdf.chapter_title(f"Iteration {counter}")

        # Add the chapter body to the PDF
        pdf.chapter_body(counter, stack, symbols,
                         dataCopy, actionList, errorList)

        # Check if the page break is needed
        if pdf.y > 180:
            pdf.add_page()

    if not errorList:
        print(f"\nTokens processed")
        for string in dataCopy:
            print(f"{string:<6}")
    else:
        print(f"\nError processing tokens")
        for error in errorList:
            print(error)

    # Output the PDF file
    pdf.output("SLRreport.pdf")


def enumerateGrammar(grammar):
    production_numbers = {}
    count = 1
    for key, values in grammar.items():
        for value in values:
            production_numbers[value] = count
            count += 1
    return production_numbers


if __name__ == '__main__':
    main()
"""


class Processor:
    def __init__(this, filename, output=None):
        try:
            this.output = output
            this.errors = False
            this.stateCount = 0
            this.result = None
            this.filename = filename
            this.file = open(filename, 'r')
            this.lines = this.file.readlines()
        except FileNotFoundError:
            raise Exception('File could not be opened')

    def compiler(this):
        this.detect_and_handle_errors()
        this.process_tokens()
        this.build_and_transform_grammar()

    def detect_and_handle_errors(this):
        errors = []

        def add_error(message):
            errors.append(message)

        def is_valid_comment(line):
            return line.startswith("/*") and not line.endswith("*/")

        def is_valid_token(line):
            return line.startswith("%") and line != '%%'

        def is_valid_token_declaration(line):
            return line.startswith("%token")

        def is_valid_ignore(line):
            return line.startswith("IGNORE")

        def is_missing_mark(line):
            return line == '%%'
        exist = False
        for i, line in enumerate(this.lines):
            line = line.strip()

            if is_valid_comment(line):
                add_error("Invalid comment format")

            if line.endswith("*/") and not line.startswith("/*"):
                add_error("Invalid comment format")

            if is_valid_token(line):
                if exist:
                    add_error("Invalid token")
                if is_valid_token_declaration(line):
                    words = line.split()
                    if len(words) < 2:
                        add_error("Unidentified %token")
                else:
                    add_error("Invalid 'token' format")
            if 'token' in line and not line.startswith("%"):
                add_error("Invalid '%token' format")
            if is_valid_ignore(line):
                words = line.split()
                if len(words) < 2:
                    add_error("Unidentified 'IGNORE'")
            if is_missing_mark(line):
                exist = True
        if not exist:
            add_error("Missing '%%' mark")
        if errors:
            error_message = "\n".join(set(errors))
            raise Exception(error_message)
        return None

    def process_tokens(this):
        tokens = set()
        ignored_tokens = set()
        all_tokens_present = True
        with open('Productions/tokens.txt', 'r') as file:
            file_tokens = {line.strip() for line in file}
        for line in this.lines:
            line = line.strip()
            if line == '%%':
                break
            if line.startswith('/*') and line.endswith('*/'):
                continue
            if line.startswith('%token'):
                line_tokens = line.split()[1:]
                tokens.update(line_tokens)
            if line.startswith('IGNORE'):
                ignored_tokens.update(line.split()[1:])
        tokens = list(tokens - ignored_tokens)
        for token in tokens:
            if token not in file_tokens:
                print(f"{token}: Not detected")
                all_tokens_present = False
        return all_tokens_present, tokens

    def build_and_transform_grammar(this):
        grammar = Grammar()
        nonTerminals = set()
        terminals = set()
        productions_found = False
        nonterm = None
        prods = []
        tempGrammar = None
        newInitialState = None

        for line in this.lines:
            line = line.strip()
            if not productions_found:
                if line == '%%':
                    productions_found = True
                continue
            if line.endswith(":"):
                if nonterm is not None:
                    grammar.productions[nonterm] = prods
                    nonTerminals.add(nonterm)
                nonterm = line[:-1].strip()
                prods = []
            elif line and not line.startswith('/*') and line != ';':
                productions = [prod.strip()
                               for prod in line.split("|") if prod.strip()]
                prods.extend(productions)
                for prod in productions:
                    for symbol in prod.split():
                        if symbol.islower():
                            nonTerminals.add(symbol)
                        elif symbol != ";":
                            terminals.add(symbol)
        if nonterm is not None:
            grammar.productions[nonterm] = prods
            nonTerminals.add(nonterm)
        grammar.productions = {nonterm: [prod for prod in prods if prod != ";"]
                               for nonterm, prods in grammar.productions.items()}
        grammar.initialState = next(iter(grammar.productions.keys()))
        grammar.nonTerminals = sorted(nonTerminals)
        grammar.terminals = sorted(terminals)
        tempGrammar = copy.deepcopy(grammar)
        newInitialState = tempGrammar.initialState + "'"
        if newInitialState in tempGrammar.productions:
            tempGrammar.productions[newInitialState].insert(
                0, tempGrammar.initialState)
            tempGrammar.productions.move_to_end(newInitialState, last=False)
        else:
            tempGrammar.productions = OrderedDict(
                [(newInitialState, [tempGrammar.initialState])] + list(tempGrammar.productions.items()))
        return tempGrammar

    def format_set(this, set_obj):
        label = "State {}\n".format_set(set_obj.state)
        for key, value in set_obj.productions.items():
            if key in set_obj.heart:
                label += "*** "
            production_str = ' | '.join(value)
            label += "{} -> {}\n".format_set(key, production_str)
        return label

    def compute_symbols(this, values):
        symbols = set()
        for production_set in values.productions.values():
            for production in production_set:
                parts = production.split()
                for part in parts:
                    if '.' in part:
                        symbol = part[1:] if part.startswith(
                            '.') else part.split()[0]
                        symbols.add(symbol)
        return list(symbols)

    def build_automata(this, firstSet):
        machine = Machine(firstSet.state, [0])
        unique_hearts = set()
        sets = [firstSet]
        unique_hearts.add(frozenset(firstSet.heart.items()))
        for set_obj in sets:
            symbols = this.compute_symbols(set_obj)
            for symbol in symbols:
                newSet = this.irA(set_obj, symbol)
                newSet_heart = frozenset(newSet.heart.items())
                if newSet_heart not in unique_hearts:
                    newSet.state = this.stateCount
                    this.stateCount += 1
                    sets.append(newSet)
                    unique_hearts.add(newSet_heart)
                    transition = Transition(set_obj, symbol, newSet)
                    machine.transitions.append(transition)
                else:
                    next_state_index = next(i for i, s in enumerate(sets) if frozenset(
                        s.heart.items()) == newSet_heart)
                    next_state = sets[next_state_index]
                    transition = Transition(set_obj, symbol, next_state)
                    machine.transitions.append(transition)
        graph = pydot.Dot(graph_type='digraph')
        for set_obj in sets:
            label = this.format_set(set_obj)
            node = pydot.Node(label)
            graph.add_node(node)
        for transition in machine.transitions:
            state = this.format_set(transition.state)
            next_state = this.format_set(transition.next)
            edge = pydot.Edge(state, next_state, label=transition.symbol)
            graph.add_edge(edge)
        for transition in machine.transitions[::-1]:
            if transition.state.state == 1:
                state = this.format_set(transition.state)
                next_state = 'accept'
                edge = pydot.Edge(state, next_state, label='$')
                graph.add_edge(edge)
                break
            elif transition.next.state == 1:
                state = this.format_set(transition.next)
                next_state = 'accept'
                edge = pydot.Edge(state, next_state, label='$')
                graph.add_edge(edge)
                break
        graph.write_pdf('LR0.pdf')
        machine.finalState = {'accept'}
        machine.display()
        this.result = machine
        return this.result

    def create_table(this):
        grammar_productions = this.grammar.productions
        terminals = this.grammar.terminals
        nonTerminals = this.grammar.nonTerminals
        follow = this.grammar.follow
        lr0 = this.automata
        augmented_header = this.grammar.initialState + "'"
        action = {}
        goTo = {}
        lr0.getTransitionStates()
        for state in lr0.states:
            state_number = state.state
            if state_number not in action:
                action[state_number] = {}
            if state_number not in goTo:
                goTo[state_number] = {}
            if state_number == 1:
                action[state_number]['$'] = 'acc'
            for transition in lr0.transitions:
                if transition.state == state:
                    if transition.symbol == '$':
                        action[state_number]['$'] = 'acc'
                    elif transition.symbol in terminals:
                        action[state_number][transition.symbol] = 's' + \
                            str(transition.next.state)
                    elif transition.symbol in nonTerminals:
                        goTo[state_number][transition.symbol] = transition.next.state
            for production_key, production_values in state.productions.items():
                if production_key != augmented_header:
                    for production in production_values:
                        if production.endswith('.'):
                            key = production_key
                            follow_set = follow[key]
                            reduced_production = production[:-1]
                            production_numbers = {}
                            count = 1
                            for key, values in grammar_productions.items():
                                for value in values:
                                    production_numbers[value] = count
                                    count += 1
                            production_number = production_numbers[reduced_production]
                            for terminal in follow_set:
                                existing_action = action[state_number].get(
                                    terminal)
                                if existing_action is not None:
                                    if existing_action.startswith('r') and existing_action != 'r' + str(production_number):
                                        raise Exception(
                                            "Conflict: Reduce-Shift conflict in state {} and symbol {}".format(state_number, terminal))
                                    elif existing_action.startswith('s') and existing_action != 's' + str(production_number):
                                        raise Exception(
                                            "Conflict: Shift-Reduce conflict in state {} and symbol {}".format(state_number, terminal))
                                else:
                                    action[state_number][terminal] = 'r' + \
                                        str(production_number)

        return action, goTo

    def draw_table(this, output):
        terminals = this.grammar.terminals.copy()
        terminals.append('$')
        nonTerminals = this.grammar.nonTerminals
        state_width = max(len(str(state))
                          for state in this.actionTable.keys()) + 2
        act_width = max(len(term) for term in terminals) + 2
        goto_width = max(len(nt) for nt in nonTerminals) + 2
        # Create a new PDF object with landscape orientation
        pdf = FPDF(orientation='L')
        # Set up the document
        pdf.set_title("SLR Table")
        pdf.set_font("Arial", size=12)
        # Add a new page
        pdf.add_page()
        # Define cell width and height
        cell_width = 20
        cell_height = 10
        # Create and format the table
        table = [["state", "act"] + terminals + ["", "goto"] + nonTerminals]
        for state, actions in this.actionTable.items():
            action_values = [actions.get(term, '') for term in terminals]
            goto_values = [this.goToTable[state].get(
                nt, '') for nt in nonTerminals]
            row = [str(state), ''] + action_values + ['', ''] + goto_values
            table.append(row)
        # Add table data to the PDF
        for row in table:
            for cell in row:
                pdf.cell(cell_width, cell_height, str(cell), border=1)
            pdf.ln(cell_height)
        # Save the PDF to the output file
        pdf.output(output)

    def generateOutput(this, output):
        with open(output, 'w') as file:
            file.write(HEADER + "\n\n")
            file.write(PDFCLASS + "\n\n")
            file.write(BODY)
