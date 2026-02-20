"""
Management command to seed the database with Georgia Standards biology topics.
Covers S7L1 through S7L5 with expected concepts and common misconceptions.

Usage:
    python manage.py seed_topics
"""

from django.core.management.base import BaseCommand
from recall.models import Topic, ConceptTag


TOPICS = [
    # ── S7L1: Diversity of Living Organisms ──────────────
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
    },
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
