from dataclasses import dataclass, field


@dataclass(frozen=True)
class CategorySeed:
    name: str
    slug: str
    description: str


@dataclass(frozen=True)
class ProductSeed:
    name: str
    slug: str
    category_slug: str
    description: str
    price_bani: int
    weight_grams: int
    stock: int
    ingredients: tuple[str, ...] = field(default_factory=tuple)


CATEGORIES: tuple[CategorySeed, ...] = (
    CategorySeed(
        "Jams",
        "jams",
        "Sun-ripened fruit, cooked slowly until the whole house smells like summer.",
    ),
    CategorySeed(
        "Preserves",
        "preserves",
        "Whole fruit in clear syrup, made from the recipes Mum knows by heart.",
    ),
    CategorySeed(
        "Fruit Butters",
        "fruit-butters",
        "Simmered for hours over a low fire with no added sugar, thick enough to hold a spoon upright.",
    ),
    CategorySeed(
        "Seasonal Editions",
        "seasonal-editions",
        "Small batches, made only while the fruit is in season.",
    ),
)

PRODUCTS: tuple[ProductSeed, ...] = (
    ProductSeed(
        "Apricot Jam",
        "apricot-jam",
        "jams",
        "Apricots from the family orchard, cooked with a little sugar and a slice of lemon. Sweet and tangy, with real pieces of fruit.",
        2450,
        370,
        24,
        ("apricots", "sugar", "lemon"),
    ),
    ProductSeed(
        "Strawberry Jam",
        "strawberry-jam",
        "jams",
        "June strawberries, cooked quickly to keep their bright colour and garden-fresh taste.",
        2600,
        370,
        18,
        ("strawberries", "sugar", "lemon"),
    ),
    ProductSeed(
        "Raspberry Jam",
        "raspberry-jam",
        "jams",
        "Mountain raspberries, seeds and all. Made for pancakes and sweet bread.",
        2900,
        370,
        12,
        ("raspberries", "sugar"),
    ),
    ProductSeed(
        "Wild Blueberry Jam",
        "wild-blueberry-jam",
        "jams",
        "Wild blueberries from the Brașov mountains, dark and full of flavour.",
        3200,
        370,
        10,
        ("wild blueberries", "sugar", "lemon"),
    ),
    ProductSeed(
        "Blackcurrant Jam",
        "blackcurrant-jam",
        "jams",
        "Intense and slightly tart, perfect next to an aged cheese.",
        2800,
        220,
        8,
        ("blackcurrants", "sugar"),
    ),
    ProductSeed(
        "Sour Cherry Preserve",
        "sour-cherry-preserve",
        "preserves",
        "Pitted sour cherries in a ruby-clear syrup. Traditionally served with a glass of cold water.",
        3000,
        370,
        15,
        ("sour cherries", "sugar"),
    ),
    ProductSeed(
        "Quince Preserve",
        "quince-preserve",
        "preserves",
        "Thin, fragrant slices of quince with a vanilla pod and lemon zest.",
        2700,
        370,
        14,
        ("quinces", "sugar", "lemon", "vanilla"),
    ),
    ProductSeed(
        "Rose Petal Preserve",
        "rose-petal-preserve",
        "preserves",
        "Petals of preserving roses, picked in the early morning. One spoonful and summer is in your glass.",
        3500,
        220,
        6,
        ("rose petals", "sugar", "lemon"),
    ),
    ProductSeed(
        "Green Walnut Preserve",
        "green-walnut-preserve",
        "preserves",
        "Young walnuts picked green in June and soaked for days. Mum's most painstaking recipe.",
        3900,
        220,
        5,
        ("green walnuts", "sugar", "cloves"),
    ),
    ProductSeed(
        "Plum Butter",
        "plum-butter",
        "fruit-butters",
        "Plums cooked all day in a copper cauldron with no sugar. Thick and dark, the old-fashioned way.",
        2500,
        370,
        30,
        ("plums",),
    ),
    ProductSeed(
        "Apple Butter with Cinnamon",
        "apple-butter-with-cinnamon",
        "fruit-butters",
        "Baked and puréed Jonathan apples with cinnamon. Great on toast or in a pie.",
        2200,
        370,
        20,
        ("apples", "cinnamon"),
    ),
    ProductSeed(
        "Fig and Walnut Jam",
        "fig-and-walnut-jam",
        "seasonal-editions",
        "Ripe figs with walnut pieces, made only in autumn and only a few dozen jars a year.",
        4200,
        220,
        4,
        ("figs", "sugar", "walnuts", "lemon"),
    ),
    ProductSeed(
        "Rosehip Jam",
        "rosehip-jam",
        "seasonal-editions",
        "Rosehips picked after the first frost and cleaned one by one. Rich in vitamin C.",
        3600,
        220,
        0,
        ("rosehips", "sugar"),
    ),
)
