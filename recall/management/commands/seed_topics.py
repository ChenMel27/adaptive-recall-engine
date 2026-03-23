"""
Management command to seed the database with Georgia Standards biology topics.
Covers S7L1 through S7L5 with expected concepts, common misconceptions,
expected reasoning patterns, supportive follow-up prompts, and concise explanations.

Usage:
    python manage.py seed_topics
"""

from django.core.management.base import BaseCommand
from recall.models import Topic, ConceptTag


TOPICS = [
    # ── S7L2: Cells & Organelles ─────────────────────────
    {
        "name": "Cells & Organelles",
        "standard": "S7L2",
        "description": "Cell structures, organelles, and their functions. Differences between plant and animal cells. Prokaryotic vs. eukaryotic cells.",
        "expected_concepts": [
            "Cell membrane controls what enters and exits the cell",
            "Nucleus contains DNA and controls cell activities",
            "Mitochondria produce energy (ATP) through cellular respiration",
            "Chloroplasts capture sunlight for photosynthesis (plant cells only)",
            "Cell wall provides structure and support (plant cells only)",
            "Ribosomes make proteins",
            "Vacuoles store water, nutrients, and waste",
            "Plant cells have chloroplasts, cell walls, and large central vacuoles",
            "Animal cells lack cell walls and chloroplasts",
            "Prokaryotic cells lack a nucleus; eukaryotic cells have a nucleus",
        ],
        "common_misconceptions": [
            "Cells are flat and two-dimensional (they are actually 3D)",
            "Only plant cells have cell membranes (both plant and animal cells do)",
            "Mitochondria are only in animal cells (they are in both plant and animal cells)",
            "The cell wall and cell membrane are the same thing",
            "All cells look the same regardless of function",
        ],
        "expected_reasoning_patterns": [
            "Explain the relationship between an organelle's structure and its function",
            "Compare and contrast plant and animal cells by explaining WHY they differ",
            "Describe how multiple organelles work together to keep a cell alive",
            "Explain the causal relationship between a cell lacking an organelle and what would happen",
        ],
        "supportive_followup_prompts": [
            "If a cell couldn't control what enters and exits, what do you think would happen to it?",
            "You mentioned some organelles — can you explain what job each one does inside the cell?",
            "What makes a plant cell different from an animal cell, and why do those differences matter?",
            "There are two big categories of cells based on whether they have a nucleus. Can you describe them?",
        ],
        "concise_explanations": [
            "The cell membrane is like a security gate — it decides what gets in and out of the cell to keep it healthy.",
            "Mitochondria are found in BOTH plant and animal cells because all living cells need energy to survive.",
            "The cell wall is an extra rigid layer OUTSIDE the cell membrane — they're different structures with different jobs.",
            "Plant cells have chloroplasts to make food from sunlight, but animal cells don't — animals get food by eating.",
        ],
    },
    # ── S7L1: Diversity of Living Organisms ──────────────
    {
        "name": "Diversity of Living Organisms",
        "standard": "S7L1",
        "description": "Classification of organisms, taxonomy, characteristics of the six kingdoms, and how organisms are scientifically compared.",
        "expected_concepts": [
            "Organisms are classified into groups based on shared characteristics",
            "The levels of classification: Domain, Kingdom, Phylum, Class, Order, Family, Genus, Species",
            "The three domains are Bacteria, Archaea, and Eukarya",
            "Scientists use dichotomous keys to identify organisms",
            "Organisms can be unicellular or multicellular",
            "Organisms can be autotrophs (make own food) or heterotrophs (consume food)",
            "Binomial nomenclature uses genus and species names",
            "Structural and behavioral adaptations help organisms survive",
        ],
        "common_misconceptions": [
            "All bacteria are harmful (many bacteria are beneficial)",
            "Fungi are plants (fungi are their own kingdom)",
            "Classification groups never change (they are updated as new evidence is found)",
            "Organisms in the same kingdom are very similar (there is great diversity within kingdoms)",
        ],
        "expected_reasoning_patterns": [
            "Explain WHY scientists classify organisms into groups rather than just listing them",
            "Describe the hierarchical relationship between classification levels (broader to more specific)",
            "Compare autotrophs and heterotrophs by explaining how each gets energy",
            "Explain how adaptations connect to an organism's survival in its environment",
        ],
        "supportive_followup_prompts": [
            "Scientists organize all living things into a system with different levels. Can you name any of those levels in order?",
            "Why do you think scientists bother classifying organisms instead of just studying each one individually?",
            "Some organisms make their own food and some have to eat other things. Can you explain the difference?",
            "What tool do scientists use to figure out what kind of organism they're looking at, step by step?",
        ],
        "concise_explanations": [
            "Classification helps scientists organize millions of species so they can study and compare them more easily.",
            "Bacteria aren't all bad — many help us digest food, and some are used to make yogurt and cheese!",
            "Fungi like mushrooms might look like plants, but they can't make their own food — they break down dead things instead.",
            "Binomial nomenclature gives every species a two-part scientific name (like Homo sapiens) so scientists worldwide use the same name.",
        ],
    },
    # ── S7L2: Cells, Tissues, Organs, Organ Systems ─────
    {
        "name": "Levels of Organization",
        "standard": "S7L2",
        "description": "How cells, tissues, organs, and organ systems work together to maintain the basic needs of organisms.",
        "expected_concepts": [
            "Cells are the basic unit of life",
            "Tissues are groups of similar cells working together",
            "Organs are made of different tissues working together",
            "Organ systems are groups of organs working together",
            "The levels of organization: cell → tissue → organ → organ system → organism",
            "Different cell types have specialized functions",
            "Homeostasis is maintaining a stable internal environment",
            "The body's organ systems interact with each other",
        ],
        "common_misconceptions": [
            "All cells in the body are the same (cells are specialized)",
            "Organs work independently without interacting",
            "A tissue is the same as an organ",
            "Homeostasis means the body stays exactly the same at all times",
        ],
        "expected_reasoning_patterns": [
            "Explain the progression from cells to organism as a building-up process",
            "Describe how organ systems depend on each other with a specific example",
            "Explain why specialized cells are important rather than having all cells be the same",
            "Describe homeostasis as a dynamic balancing process, not a fixed state",
        ],
        "supportive_followup_prompts": [
            "Can you walk me through the levels of organization in order, starting from the smallest?",
            "Why can't organs do their job all by themselves — what else do they need?",
            "What does it mean when we say the body tries to stay 'balanced'? Can you give an example?",
            "If all your cells were exactly the same, what problems might your body have?",
        ],
        "concise_explanations": [
            "A tissue is a group of SIMILAR cells doing the same job, while an organ is made of DIFFERENT tissues working together — like how your heart has muscle tissue, nerve tissue, and blood tissue.",
            "Homeostasis doesn't mean your body never changes — it means your body is always making adjustments to stay in a healthy range, like a thermostat.",
            "Your organ systems are like a team — the digestive system breaks down food, but the circulatory system has to deliver those nutrients to every cell.",
            "Cells specialize so they can be really good at one job — a nerve cell is shaped differently from a muscle cell because they do totally different things.",
        ],
    },
    # ── S7L3: Reproduction & Genetics ────────────────────
    {
        "name": "Reproduction & Genetics",
        "standard": "S7L3",
        "description": "Sexual and asexual reproduction, DNA, genes, chromosomes, inherited vs. acquired traits, and genetic variation.",
        "expected_concepts": [
            "Asexual reproduction involves one parent and produces genetically identical offspring",
            "Sexual reproduction involves two parents and produces genetically unique offspring",
            "DNA carries genetic information in chromosomes",
            "Genes are segments of DNA that code for specific traits",
            "Inherited traits are passed from parents to offspring through genes",
            "Acquired traits are developed during an organism's lifetime and are not inherited",
            "Sexual reproduction increases genetic variation",
            "Mitosis produces two identical cells for growth and repair",
            "Meiosis produces sex cells (gametes) with half the chromosomes",
            "Dominant and recessive alleles determine trait expression",
        ],
        "common_misconceptions": [
            "Acquired traits (like muscles from exercise) can be inherited",
            "Asexual reproduction always produces weaker offspring",
            "DNA and genes are different things (genes are part of DNA)",
            "All traits are determined by a single gene",
            "Dominant traits are always more common than recessive traits",
        ],
        "expected_reasoning_patterns": [
            "Explain the cause-and-effect relationship between sexual reproduction and genetic variation",
            "Distinguish between inherited and acquired traits with reasoning, not just examples",
            "Describe how DNA, genes, and chromosomes relate to each other (part-to-whole)",
            "Explain WHY genetic variation matters for a population's survival",
        ],
        "supportive_followup_prompts": [
            "What's the difference between a trait you're born with and a trait you develop during your life?",
            "Why does sexual reproduction lead to more variety in offspring than asexual reproduction?",
            "DNA, genes, and chromosomes are all related. Can you explain how they fit together?",
            "There are two types of cell division. Can you describe what each one is used for?",
        ],
        "concise_explanations": [
            "Genes are actually PART of DNA — think of DNA as a long instruction book, and genes are individual instructions within it.",
            "If you build big muscles from exercise, your kids won't automatically have big muscles — that's an acquired trait, not an inherited one.",
            "'Dominant' doesn't mean 'more common' — it means that allele shows up when you have at least one copy of it. A recessive trait can still be very common in a population.",
            "Sexual reproduction mixes DNA from two parents, creating unique combinations — this variation helps populations survive when the environment changes.",
        ],
    },
    # ── S7L4: Ecosystems & Interdependence ───────────────
    {
        "name": "Ecosystems & Interdependence",
        "standard": "S7L4",
        "description": "Ecosystems, food webs, energy flow, symbiotic relationships, cycling of matter, and human impact on ecosystems.",
        "expected_concepts": [
            "Energy flows through ecosystems from producers to consumers to decomposers",
            "Producers (autotrophs) make their own food through photosynthesis",
            "Consumers (heterotrophs) get energy by eating other organisms",
            "Decomposers break down dead organisms and recycle nutrients",
            "Food webs show interconnected food chains in an ecosystem",
            "Energy decreases as it moves up trophic levels (10% rule)",
            "Symbiotic relationships: mutualism, commensalism, parasitism",
            "Matter is recycled through ecosystems (water cycle, carbon cycle, nitrogen cycle)",
            "Changes in one part of an ecosystem affect the whole system",
            "Human activities can disrupt ecosystems",
        ],
        "common_misconceptions": [
            "Energy is recycled in ecosystems (energy flows, matter is recycled)",
            "Decomposers are not important to ecosystems",
            "All relationships between organisms are competitive",
            "Food chains are linear and simple (food webs are complex networks)",
            "Removing one species from a food web has no effect on others",
        ],
        "expected_reasoning_patterns": [
            "Distinguish between energy flow (one-way) and matter cycling (recycled) in ecosystems",
            "Explain the ripple effects of removing one organism from a food web",
            "Describe symbiotic relationships by explaining how BOTH organisms are affected",
            "Explain why energy decreases at each trophic level using the 10% rule",
        ],
        "supportive_followup_prompts": [
            "Energy and matter both move through ecosystems, but they move differently. Can you explain how?",
            "What would happen to an ecosystem if all the decomposers suddenly disappeared?",
            "Can you describe a relationship between two organisms where both benefit? What about one where only one benefits?",
            "If a predator is removed from a food web, what might happen to the organisms it used to eat — and what about the organisms THEY eat?",
        ],
        "concise_explanations": [
            "Energy FLOWS through an ecosystem and gets used up (as heat), but matter like carbon and water gets RECYCLED over and over — they move in completely different ways.",
            "Without decomposers, dead plants and animals would pile up and nutrients would stay locked inside them — other organisms wouldn't be able to use those nutrients to grow.",
            "Not all organism relationships are competitive — in mutualism both species benefit, in commensalism one benefits and the other isn't affected, and in parasitism one benefits while the other is harmed.",
            "The 10% rule means that when one organism eats another, only about 10% of the energy gets passed along — the rest is used for the organism's own life activities or lost as heat.",
        ],
    },
    # ── S7L5: Evolution ──────────────────────────────────
    {
        "name": "Evolution & Natural Selection",
        "standard": "S7L5",
        "description": "Theory of evolution, natural selection, adaptation, fossil evidence, and how inherited characteristics change over time.",
        "expected_concepts": [
            "Evolution is the change in inherited characteristics of a population over time",
            "Natural selection is the process where organisms with favorable traits survive and reproduce more",
            "Variation exists within populations due to genetic differences",
            "Adaptations are traits that help organisms survive in their environment",
            "Fossil evidence supports the theory of evolution",
            "Organisms with similar structures may share a common ancestor (homologous structures)",
            "Environmental changes can drive natural selection",
            "Evolution occurs in populations, not individuals",
            "Organisms do not choose to evolve or adapt",
        ],
        "common_misconceptions": [
            "Individual organisms can evolve during their lifetime",
            "Organisms choose to adapt or evolve on purpose",
            "Evolution means one species turns into another species suddenly",
            "Humans evolved from modern monkeys (humans and monkeys share a common ancestor)",
            "Only the strongest survive (fitness means reproductive success, not physical strength)",
            "Evolution is 'just a theory' (scientific theories are well-supported explanations)",
        ],
        "expected_reasoning_patterns": [
            "Explain natural selection as a multi-step process (variation → selection pressure → survival → reproduction)",
            "Distinguish between individual change and population-level evolution",
            "Explain how environmental change drives natural selection with a cause-and-effect chain",
            "Use fossil evidence or homologous structures to support an argument about common ancestry",
        ],
        "supportive_followup_prompts": [
            "Can an individual animal evolve during its own lifetime, or does evolution work differently? Explain your thinking.",
            "Imagine the climate in a habitat suddenly gets much colder. How might that change which organisms survive?",
            "Scientists sometimes find similar bone structures in very different animals. What might that tell us?",
            "People sometimes say 'survival of the fittest.' What does 'fitness' actually mean in science?",
        ],
        "concise_explanations": [
            "An individual organism can't evolve — evolution is a change that happens across a whole population over many generations as certain traits become more or less common.",
            "Animals don't 'choose' to adapt — instead, individuals with traits that happen to help them survive are more likely to have babies, and those helpful traits get passed along.",
            "Humans didn't evolve from today's monkeys — instead, humans and monkeys share a distant ancestor that lived millions of years ago, and both groups changed over time.",
            "In science, 'fitness' doesn't mean being strong — it means how successful an organism is at surviving AND reproducing. A small, camouflaged animal can be more 'fit' than a large, visible one.",
        ],
    },
]


class Command(BaseCommand):
    help = "Seed the database with Georgia Standards biology topics (S7L1–S7L5)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Delete all existing topics before seeding.",
        )

    def handle(self, *args, **options):
        if options["clear"]:
            count = Topic.objects.count()
            Topic.objects.all().delete()
            self.stdout.write(self.style.WARNING(f"Deleted {count} existing topics."))

        created_count = 0
        for data in TOPICS:
            topic, created = Topic.objects.get_or_create(
                name=data["name"],
                standard=data["standard"],
                defaults={
                    "description": data["description"],
                    "expected_concepts": data["expected_concepts"],
                    "common_misconceptions": data["common_misconceptions"],
                    "expected_reasoning_patterns": data.get("expected_reasoning_patterns", []),
                    "supportive_followup_prompts": data.get("supportive_followup_prompts", []),
                    "concise_explanations": data.get("concise_explanations", []),
                },
            )
            if created:
                created_count += 1
                # Also create ConceptTag entries for each expected concept
                for concept in data["expected_concepts"]:
                    ConceptTag.objects.get_or_create(
                        topic=topic,
                        name=concept,
                        defaults={"is_misconception": False},
                    )
                for misconception in data["common_misconceptions"]:
                    ConceptTag.objects.get_or_create(
                        topic=topic,
                        name=misconception,
                        defaults={"is_misconception": True},
                    )
                self.stdout.write(f"  ✓ Created: [{topic.standard}] {topic.name}")
            else:
                self.stdout.write(f"  – Exists:  [{topic.standard}] {topic.name}")

        self.stdout.write(
            self.style.SUCCESS(f"\nDone! {created_count} new topics created ({len(TOPICS)} total defined).")
        )
