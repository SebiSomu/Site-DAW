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
    price_cents: int
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
        "Whole fruit packed in thick syrup, made from the recipes Mum knows by heart.",
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
        "Peach Jam",
        "peach-jam",
        "jams",
        "Ripe summer peaches cut into thick slices and cooked gently with a little sugar and lemon. Soft, golden and full of fruit.",
        2650,
        370,
        16,
        ("peaches", "sugar", "lemon"),
    ),
    ProductSeed(
        "Cherry Plum Jam",
        "cherry-plum-jam",
        "jams",
        "Small cherry plums, golden and blush red, cooked whole in a light syrup. Tangy and bright, a jam for the first days of July.",
        2500,
        370,
        14,
        ("cherry plums", "sugar"),
    ),
    ProductSeed(
        "Forest Fruit Jam",
        "forest-fruit-jam",
        "jams",
        "Blackberries, raspberries, wild blueberries and a handful of wild strawberries, cooked together into one deep crimson jam.",
        3100,
        370,
        9,
        ("blackberries", "raspberries", "wild blueberries", "wild strawberries", "sugar"),
    ),
    ProductSeed(
        "Sour Cherry Preserve",
        "sour-cherry-preserve",
        "preserves",
        "Pitted sour cherries packed in a thick, dark ruby syrup. Traditionally served with a glass of cold water.",
        3000,
        370,
        15,
        ("sour cherries", "sugar"),
    ),
    ProductSeed(
        "Quince Preserve",
        "quince-preserve",
        "preserves",
        "Fragrant slices of quince cooked soft in a thick syrup with a vanilla pod and lemon zest.",
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
        "Pear and Vanilla Butter",
        "pear-and-vanilla-butter",
        "fruit-butters",
        "Ripe pears cooked slowly with a whole vanilla pod and no added sugar. Smooth, mellow and soft enough to spread without a knife.",
        2400,
        370,
        22,
        ("pears", "vanilla"),
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
    ProductSeed(
        "Lingonberry Jam",
        "lingonberry-jam",
        "seasonal-editions",
        "Tart little mountain lingonberries, cooked whole until they just soften. Made only in late autumn, and wonderful with roast meat or cheese.",
        3400,
        220,
        7,
        ("lingonberries", "sugar"),
    ),
    ProductSeed(
        "Orange Marmalade",
        "orange-marmalade",
        "seasonal-editions",
        "Thin shreds of orange peel in a glowing amber jelly, cooked in the first cold months when the oranges are at their best.",
        2300,
        370,
        20,
        ("oranges", "sugar", "lemon"),
    ),
    ProductSeed(
        "Lemon and Ginger Marmalade",
        "lemon-and-ginger-marmalade",
        "seasonal-editions",
        "Pale golden lemon marmalade with fine shreds of peel and a little fresh ginger. Sharp, warming and made for winter mornings.",
        2800,
        220,
        18,
        ("lemons", "ginger", "sugar"),
    ),
)
