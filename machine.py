import copy
from queue import LifoQueue  # For stack operations
import re
import graphviz as gv


# Machine class
class Machine:
    def __init__(this, startingState, finalState):
        this.transitions = []
        this.startingState = startingState
        this.finalState = finalState
        this.states = []

    def getFinalMachineState(this):
        return this.finalState

    def getInitialMachineState(this):
        return this.startingState

    def getStates(this):
        states = []
        for transition in this.transitions:
            if transition.state not in states:
                states.append(transition.state)
            if transition.next not in states:
                states.append(transition.next)
        this.states = sorted(states)

    def getTransitionStates(this):
        states = []
        for transition in this.transitions:
            if transition.state.state not in states:
                states.append(transition.state)
            if transition.next.state not in states:
                states.append(transition.next)
        this.states = states

    def display(this):
        states = []
        for transition in this.transitions:
            if transition.state not in states:
                states.append(transition.state)
            if transition.next not in states:
                states.append(transition.next)


# State class
class State:
    def __init__(this, state_id):
        this.state_id = state_id

    def __repr__(this):
        return str(this.state_id)


# Transitions class
class Transition:
    def __init__(this, state, symbol, next):
        this.state = state
        this.next = next
        this.symbol = symbol


# Graph class
class Graph:
    def __init__(this, transitions, startingState, finalState, title=None):
        this.transitions = transitions
        this.startingState = startingState
        this.finalState = finalState
        this.graph = gv.Digraph(graph_attr={'rankdir': 'LR'})

        for transition in this.transitions:
            this.graph.edge(str(transition.state), str(
                transition.next_state), label=transition.symbol)

        this.graph.node(str(startingState), shape='circle', style='bold')
        this.graph.node('start', shape='point')
        this.graph.edge('start', str(startingState), arrowhead='normal')

        for final_state in finalState:
            this.graph.node(str(final_state), shape='doublecircle')

        if title:
            this.graph.node('title', label=title, shape='none',
                            fontsize='20', fontcolor='black', fontname='Arial')

    def draw(this, filename='NFA'):
        return this.graph.view(filename=filename)


# Clase Node based in a node from Linked List
# https://www.tutorialspoint.com/python_data_structure/python_linked_lists.htm
class Node(object):
    # Node class with parents, right node, left node, symbols
    def __init__(this, symbol, parent, prev, next):
        this.symbol = symbol
        this.parent = parent
        this.prev = prev
        this.next = next
        this.nullable = False
        this.firstpos = []
        this.lastpos = []
        this.followpos = []
        this.pos = None


# Stack class with stack functions
# Import LastInFirstOut
# https://codefather.tech/blog/create-stack-python/#:~:text=To%20create%20a%20stack%20in%20Python%20you%20can%20use%20a,the%20top%20of%20the%20stack.
class Stack:
    def __init__(this):
        this.stack = []

    def is_empty(this):
        return not this.stack

    def peek(this):
        return this.stack[-1] if not this.is_empty() else "$"

    def pop(this):
        return this.stack.pop() if not this.is_empty() else "$"

    def push(this, op):
        this.stack.append(op)


# Set class
class Set:
    def __init__(this):
        this.heart = {}
        this.productions = {}
        this.rest = {}
        this.state = 0

    def getHeart(this):
        return this.heart

    def getRest(this):
        return this.rest

    def getProductions(this):
        return this.productions


# Tokens class
class Tokens():
    def __init__(this):
        this.tokens = []

    # Regex defined as bucle
    def tokenize(this, file):
        with open(file, 'r') as f:
            archiveLines = f.read()
        variables = re.findall(r'\s*(\w+)\s*{', archiveLines)
        tokenStrip = r'let\s+([a-zA-Z0-9_-]+)\s+=\s+(.*)'
        for line in archiveLines.splitlines():
            match = re.match(tokenStrip, line.strip())
            if match and match.group(1) in variables:
                this.tokens.append((match.group(1), match.group(2)))
        return this.tokens


# LRParser class
'''
grammar = {
    'S': ['A B', 'C'],
    'A': ['a A', 'b'],
    'B': ['c'],
    'C': ['d', '']
}

S -> A B | C
A -> a A | b
B -> c
C -> d | ε

parser = Parser(grammar, symbols)

first = parser.first(symbol)
result = result.union(parser.goto(no_terminal))
closure = parser.closure(items)

'''


# Grammar class
class Grammar:
    def __init__(this):
        this.initialState = None
        this.terminals = []
        this.nonTerminals = []
        this.first = {}
        this.follow = {}
        this.productions = {}

    def getTerminals(this):
        return this.terminals

    def getNonTerminals(this):
        return this.nonTerminals

    def getInitialState(this):
        return this.initialState

    def getProductions(this):
        return this.productions


# Parser class
class Parser:
    def __init__(this, cannonGrammar):
        this.cannonGrammar = cannonGrammar

    def closure(this, I):
        J = copy.deepcopy(I)
        added = True
        while added:
            added = False
            productions_copy = dict(J.productions)
            for key, value in productions_copy.items():
                for prod in value:
                    parts = prod.split()
                    for part in parts:
                        if '.' in part:
                            if part[-1] == '.':
                                next_part_idx = parts.index(part) + 1
                                if next_part_idx == len(parts) or parts[next_part_idx] in this.cannonGrammar.terminals:
                                    continue
                                else:
                                    part = parts[next_part_idx]
                            concat = part.replace('.', '')
                            if concat in this.cannonGrammar.productions:
                                for new_prod in this.cannonGrammar.productions[concat]:
                                    new_item = '.' + new_prod
                                    if new_item not in J.productions.setdefault(concat, []):
                                        J.productions.setdefault(
                                            concat, []).append(new_item)
                                        J.rest.setdefault(
                                            concat, []).append(new_item)
                                        added = True
        return J

    def goto(this, I, X):
        J = Set()
        I2 = copy.deepcopy(I)
        for key, value in I2.productions.items():
            for prod in value:
                parts = prod.split()
                for i, part in enumerate(parts):
                    if '.' in part:
                        if part.startswith('.'):
                            concat = part.replace('.', '')
                            if concat == X:
                                new_prod = ' '.join(
                                    [X + '.' if p == '.' + X else p for p in parts])
                                J.productions.setdefault(
                                    key, []).append(new_prod)
                                J.heart.setdefault(key, []).append(new_prod)
                        elif part.endswith('.'):
                            part_idx = parts.index(part)
                            next_part_idx = parts.index(part) + 1
                            if next_part_idx == len(parts):
                                continue
                            next_part = parts[next_part_idx]
                            sinPunt = part.replace('.', '')
                            if next_part == X:
                                next_part += '.'
                                parts[next_part_idx] = next_part
                                parts[part_idx] = sinPunt
                                new_prod = ' '.join(parts)
                                J.productions.setdefault(
                                    key, []).append(new_prod)
                                J.heart.setdefault(key, []).append(new_prod)
        return this.closure(J)

    def getSetSymbols(this, I):
        symbols = set()
        for value in I.productions.values():
            for production in value:
                parts = production.split()
                for i, part in enumerate(parts):
                    part = part.strip()
                    if not part:
                        continue
                    if '.' in part:
                        if part.startswith('.'):
                            next_symbol = part[1:]
                            symbols.add(next_symbol)
                        elif part.endswith('.'):
                            if i < len(parts) - 1:
                                next_part = parts[i+1].strip().split()[0]
                                symbols.add(next_part)
        return list(symbols)

    def compute_first(this, grammar):
        first = {nonterminal: set() for nonterminal in grammar}
        changes = True
        while changes:
            changes = False
            for nonterminal in grammar:
                for production in grammar[nonterminal]:
                    symbols = production.split()
                    for i, symbol in enumerate(symbols):
                        if symbol.isupper():
                            if symbol not in first[nonterminal]:
                                first[nonterminal].add(symbol)
                                changes = True
                            break
                        else:
                            for first_symbol in first[symbol]:
                                if first_symbol not in first[nonterminal]:
                                    first[nonterminal].add(first_symbol)
                                    changes = True
                            if 'EPSILON' not in first[symbol]:
                                break
                    else:
                        if 'EPSILON' not in first[nonterminal]:
                            first[nonterminal].add('EPSILON')
                            changes = True
        return first

    def compute_follow(this, grammar):
        follow = {nonterminal: set() for nonterminal in grammar}
        start_symbol = list(grammar.keys())[0]
        follow[start_symbol].add('$')
        first = this.compute_first(grammar)
        changes = True
        while changes:
            changes = False
            for nonterminal in grammar:
                for production in grammar[nonterminal]:
                    symbols = production.split()
                    for i, symbol in enumerate(symbols):
                        if symbol.islower():
                            if i == len(symbols) - 1:
                                for follow_symbol in follow[nonterminal]:
                                    if follow_symbol not in follow[symbol]:
                                        follow[symbol].add(follow_symbol)
                                        changes = True
                            else:
                                if symbols[i+1].islower():
                                    for first_symbol in first[symbols[i+1]]:
                                        if first_symbol != 'EPSILON' and first_symbol not in follow[symbol]:
                                            follow[symbol].add(first_symbol)
                                            changes = True
                                    if 'EPSILON' in first[symbols[i+1]]:
                                        for follow_symbol in follow[nonterminal]:
                                            if follow_symbol not in follow[symbol]:
                                                follow[symbol].add(
                                                    follow_symbol)
                                                changes = True
                                else:
                                    if symbols[i+1] not in first:
                                        first[symbols[i+1]] = {symbols[i+1]}
                                    if symbols[i+1] != 'EPSILON' and symbols[i+1] not in follow[symbol]:
                                        follow[symbol].add(symbols[i+1])
                                        changes = True
                        else:
                            continue
        return follow


# Parser class
class LR0Automaton:
    def __init__(this, grammar, symbols):
        this.grammar = grammar
        this.symbols = symbols

    def first(this, simbolo):
        if simbolo in this.grammar:
            productions = this.grammar[simbolo]
            result = set()
            for production in productions:
                first = this.first(production[0])
                result = result.union(first)
            return result
        else:
            return {simbolo}

    def goto(this, no_terminal):
        result = set()
        if no_terminal == 'S':
            result.add('$')
        for simbolo in this.grammar:
            productions = this.grammar[simbolo]
            for production in productions:
                symbols = production.split()
                if no_terminal in symbols:
                    idx = symbols.index(no_terminal)
                    if idx < len(symbols)-1:
                        first = this.first(symbols[idx+1])
                        result = result.union(first)
                    else:
                        if simbolo != no_terminal:
                            result = result.union(this.goto(simbolo))
        return result

    def closure(this, items):
        closure = items
        new_items = True
        while new_items:
            new_items = False
            for item in closure.copy():
                parts = item.split(' -> ')
                if parts[1] != '':
                    symbols = parts[1].split()
                    if symbols[0] in this.grammar:
                        firsts = this.first(symbols[1])
                        for production in this.grammar[symbols[0]]:
                            new_item = symbols[0] + ' -> . ' + production
                            if new_item not in closure:
                                new_items = True
                                closure.add(new_item)
                                closure = closure.union(
                                    this.closure({new_item}))
                        if 'ε' in firsts:
                            new_item = parts[0] + \
                                ' -> ' + ' '.join(symbols[1:])
                            if new_item not in closure:
                                new_items = True
                                closure.add(new_item)
                                closure = closure.union(
                                    this.closure({new_item}))
        return closure
