# Uvoz potrebnih modula iz Flask-a i Typing-a
from flask import Flask, jsonify, request
from typing import Optional, List

# Inicijalizacija Flask aplikacije
app = Flask(__name__)

# Definiranje klase Node koja predstavlja jedan čvor stabla
class Node:
    def __init__(self, id: int, title: str, parent_id: Optional[int] = None, ordering: int = 0):
       # Inicijalizacija atributa čvora
        self.id = id # Jedinstveni identifikator čvora
        self.title = title  # Naslov čvora
        self.parent_id = parent_id # ID roditeljskog čvora, ako postoji
        self.ordering = ordering # Redoslijed unutar roditeljskog čvora
        self.children: List[Node] = [] # Lista podređenih čvorova

    # Metoda koja pretvara čvor u rječnik, uključujući sve podređene čvorove
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'parent_id': self.parent_id,
            'ordering': self.ordering,
            'children': [child.to_dict() for child in self.children] # Rekurzivno pozivanje za sve podređene čvorove
        }

# Klasa Tree upravlja cijelom strukturom stabla
class Tree:
    def __init__(self):
        self.nodes = {} # Rječnik za pohranu svih čvorova po ID-u
        self.root = Node(id=1, title="Root Node")  # Korijenski čvor s ID-em 1
        self.nodes[1] = self.root # Dodaje korijenski čvor u rječnik čvorova

    # Metoda za dodavanje novog čvora u stablo
    def add_node(self, node: Node):
        if node.parent_id not in self.nodes:
            # Provjera postoji li roditeljski čvor, ako ne postoji, ispisuje pogrešku
            raise ValueError("Roditeljski čvor nije pronađen")
        self.nodes[node.id] = node # Dodaje novi čvor u rječnik čvorova
        self.nodes[node.parent_id].children.append(node) # Dodaje čvor kao podređeni roditelju
        self.reorder_children(node.parent_id) # Ažurira redoslijed podređenih čvorova

    # Metoda za rekurzivno brisanje čvora i svih njegovih podređenih čvorova
    def delete_node(self, node_id: int):
        node = self.nodes.get(node_id)
        if node:
            if node.parent_id is not None:
                # Ako postoji roditeljski čvor, uklanja trenutni čvor iz liste podređenih
                parent = self.nodes.get(node.parent_id)
                if parent:
                    parent.children = [child for child in parent.children if child.id != node_id]
            for child in node.children:
                # Rekurzivno brisanje svih podređenih čvorova
                self.delete_node(child.id)
            del self.nodes[node_id] # Brisanje čvora iz rječnika čvorova

    # Metoda koja vraća cijelo stablo kao rječnik
    def get_tree(self):
        return self.root.to_dict()

    # Metoda za promjenu redoslijeda podređenih čvorova unutar istog roditelja
    def reorder_children(self, parent_id: int):
        parent = self.nodes[parent_id]
        parent.children.sort(key=lambda x: x.ordering) # Sortiranje podređenih čvorova prema redoslijedu
        for index, child in enumerate(parent.children):
            child.ordering = index # Ažurira redoslijed svakog podređenog čvora

# Inicijaliziraj globalnu instancu stabla
tree = Tree()

# Endpoint za dohvat stabla
@app.route('/tree', methods=['GET'])
def get_tree():
    return jsonify(tree.get_tree()) # Vraća stablo u JSON formatu

# Endpoint za dodavanje novog čvora
@app.route('/node', methods=['POST'])
def add_node():
    data = request.json # Preuzima JSON podatke iz zahtjeva
    node = Node(id=data['id'], title=data['title'], parent_id=data.get('parent_id'), ordering=data.get('ordering', 0))
    try:
        tree.add_node(node) # Pokušava dodati novi čvor u stablo
        return jsonify({"message": "Čvor uspješno dodan"}), 201 # Vraća uspješnu poruku
    except ValueError as e:
        return jsonify({"error": str(e)}), 400 # Vraća pogrešku ako roditeljski čvor nije pronađen

# Endpoint za ažuriranje čvora
@app.route('/node/<int:id>', methods=['PUT'])
def update_node(id):
    data = request.json # Preuzima JSON podatke iz zahtjeva
    node = tree.nodes.get(id)
    if not node:
        return jsonify({"error": "Čvor nije pronađen"}), 404 # Vraća pogrešku ako čvor ne postoji
    node.title = data.get('title', node.title)  # Ažurira naslov čvora
    return jsonify({"message": "Čvor uspješno ažuriran"})

# Endpoint za brisanje čvora
@app.route('/node/<int:id>', methods=['DELETE'])
def delete_node(id):
    if id not in tree.nodes:
        return jsonify({"error": "Čvor nije pronađen"}), 404 # Vraća pogrešku ako čvor ne postoji
    tree.delete_node(id) # Briše čvor i sve njegove podređene čvorove
    return jsonify({"message": "Čvor uspješno izbrisan"})

# Endpoint za promjenu redoslijeda čvora unutar istog roditelja (BONUS zadatak)
@app.route('/node/<int:id>/reorder', methods=['POST'])
def reorder_node(id):
    data = request.json # Preuzima JSON podatke iz zahtjeva
    new_ordering = data['ordering']
    node = tree.nodes.get(id)
    if not node:
        return jsonify({"error": "Čvor nije pronađen"}), 404 # Vraća pogrešku ako čvor ne postoji
    if node.parent_id is None:
        return jsonify({"error": "Korijenski čvor se ne može premještati"}), 400 # Vraća pogrešku za korijenski čvor
    node.ordering = new_ordering  # Postavlja novi redoslijed
    tree.reorder_children(node.parent_id) # Ažurira redoslijed podređenih čvorova
    return jsonify({"message": "Čvor uspješno premješten i redoslijed ažuriran"})

# Pokretanje Flask aplikacije
if __name__ == '__main__':
    app.run(port=5000) # Pokreće server na portu 5000


"""
DATABASE OPERACIJE:

1. Dodavanje Čvora:
    INSERT INTO node (id, title, parent_node_id, ordering) 
    VALUES (new_id, 'Node Title', parent_id, ordering_value);

2. Dohvat cijelog stabla:
    SELECT * FROM node;

3. Dohvat čvora po ID-u:
    SELECT * FROM node WHERE id = node_id;

4. Ažuriranje čvora:
    UPDATE node 
    SET title = 'New Title', ordering = new_ordering 
    WHERE id = node_id;

5. Brisanje čvora:
    DELETE FROM node WHERE id = node_id;
    
- Ako treba obrisati sve podređene čvorove rekurzivno:
    DELETE FROM node WHERE parent_node_id = node_id;

6. Promjena redoslijeda čvorova:
    UPDATE node 
    SET ordering = new_ordering 
    WHERE id = node_id AND parent_node_id = parent_id;
"""