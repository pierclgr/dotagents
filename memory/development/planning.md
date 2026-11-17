# Planning

## Planning as a Q&A session
Planning is a Q&A session between the user and the agent, from start to end:
- The user takes time and asks the agent many questions to make the needs
  clear.
- The agent also asks the user many questions to make the needs clear.
- **Write the plan only after** the user has no more questions and has
  answered all the agent's questions.

## Plan contents
When writing a plan, include:

1. **Verifiable goals**: break the specs agreed with the user into concrete
   outcomes. For each goal, state what must be achieved and how to verify it.
   These goals guide implementation iterations and are separate from test
   cases. Review the goals with the user as part of the plan.
2. **Class architecture blueprint**:
   - a Mermaid class diagram of the classes and their relations. Use the UML
     relations, each arrow with a short label that names the call or the role:
     - `<|--` inheritance: a class subclasses another.
     - `..|>` realization: a class implements an abstract base or interface.
     - `*--` composition: a class creates and owns the other.
     - `o--` aggregation: a class holds a shared object that it did not create.
     - `-->` association: a class keeps the other in a field and calls it.
     - `..>` dependency: a class uses or creates the other only inside a method.
   - in a change to existing code, give each class in the diagram a status
     stereotype and a color. Always use black text (`color:#000`), so the
     text is easy to read:

     | Status | Stereotype | Style |
     |---|---|---|
     | new | `<<NEW>>` | `fill:#c8e6c9,stroke:#2e7d32,color:#000` (green) |
     | moved or renamed | `<<MOVED>>` / `<<MOVED_RENAMED>>` | `fill:#bbdefb,stroke:#1565c0,color:#000` (blue) |
     | changed | `<<CHANGED>>` | `fill:#ffe0b2,stroke:#ef6c00,color:#000` (orange) |
     | unchanged | none | no style |

     Example:
     ```mermaid
     classDiagram
         Base <|-- Child : subclasses
         <<NEW>> Child
         <<CHANGED>> Base
         style Child fill:#c8e6c9,stroke:#2e7d32,color:#000
         style Base fill:#ffe0b2,stroke:#ef6c00,color:#000
     ```
     Below the diagram, add a table with the classes of each status. List
     changed classes that are not in the diagram as text below the table.
     Do not show removed classes.
   - a blueprint of each class: fields and method signatures, with no
     implementation. Each class, field, method and has a short 
     description of what it holds or does. Example:
     ```python
     # class representing a person
     class Person:
         name: str  # first name of the person
         surname: str  # last name of the person
         birth: date  # date of birth

         @property
         def age(self) -> int: ...  # age in years, computed from birth
     ```
   - in a change to existing code, the blueprint shows only what changes:
     new and changed fields and methods, each marked `# NEW` or
     `# CHANGED`. Leave out unchanged and removed members. For a class
     that only moves to another file, write the move in one line, with no
     blueprint.
3. **Pseudocode**: pseudocode of the implementation, especially of the biggest methods, functions and code slices
