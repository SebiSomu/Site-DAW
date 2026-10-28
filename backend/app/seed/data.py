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
        "Gemuri",
        "gemuri",
        "Fructe coapte la soare, fierte încet, până când casa miroase a vară.",
    ),
    CategorySeed(
        "Dulcețuri",
        "dulceturi",
        "Fructe întregi în sirop limpede, după rețetele pe care mama le știe pe de rost.",
    ),
    CategorySeed(
        "Magiunuri",
        "magiunuri",
        "Fierte ore întregi la foc mic, fără zahăr adăugat, groase cât să stea lingurița în ele.",
    ),
    CategorySeed(
        "Ediții de sezon",
        "editii-de-sezon",
        "Borcane puține, făcute doar cât ține sezonul fructului.",
    ),
)

PRODUCTS: tuple[ProductSeed, ...] = (
    ProductSeed(
        "Gem de caise",
        "gem-de-caise",
        "gemuri",
        "Caise din livada bunicilor, fierte cu puțin zahăr și o felie de lămâie. Dulce-acrișor, cu bucăți de fruct.",
        2450,
        370,
        24,
        ("caise", "zahăr", "lămâie"),
    ),
    ProductSeed(
        "Gem de căpșuni",
        "gem-de-capsuni",
        "gemuri",
        "Căpșuni culese în iunie, fierte repede ca să-și păstreze culoarea vie și gustul de grădină.",
        2600,
        370,
        18,
        ("căpșuni", "zahăr", "lămâie"),
    ),
    ProductSeed(
        "Gem de zmeură",
        "gem-de-zmeura",
        "gemuri",
        "Zmeură de munte, cu semințele ei cu tot, pentru clătite și cozonac.",
        2900,
        370,
        12,
        ("zmeură", "zahăr"),
    ),
    ProductSeed(
        "Gem de afine",
        "gem-de-afine",
        "gemuri",
        "Afine sălbatice din Munții Brașovului, închise la culoare și pline de gust.",
        3200,
        370,
        10,
        ("afine", "zahăr", "lămâie"),
    ),
    ProductSeed(
        "Gem de coacăze negre",
        "gem-de-coacaze-negre",
        "gemuri",
        "Intens și ușor acrișor, perfect lângă o brânză maturată.",
        2800,
        220,
        8,
        ("coacăze negre", "zahăr"),
    ),
    ProductSeed(
        "Dulceață de cireșe amare",
        "dulceata-de-cirese-amare",
        "dulceturi",
        "Cireșe amare fără sâmbure, în sirop limpede ca rubinul. Se servește cu un pahar de apă rece.",
        3000,
        370,
        15,
        ("cireșe amare", "zahăr"),
    ),
    ProductSeed(
        "Dulceață de gutui",
        "dulceata-de-gutui",
        "dulceturi",
        "Fâșii subțiri de gutui, parfumate, cu o boabă de vanilie și coajă de lămâie.",
        2700,
        370,
        14,
        ("gutui", "zahăr", "lămâie", "vanilie"),
    ),
    ProductSeed(
        "Dulceață de trandafiri",
        "dulceata-de-trandafiri",
        "dulceturi",
        "Petale de trandafir de dulceață, culese dimineața. O lingură și ai vara într-un pahar.",
        3500,
        220,
        6,
        ("petale de trandafir", "zahăr", "lămâie"),
    ),
    ProductSeed(
        "Dulceață de nuci verzi",
        "dulceata-de-nuci-verzi",
        "dulceturi",
        "Nuci culese crude, în iunie, lăsate la înmuiat zile întregi. Rețeta cea mai migăloasă a mamei.",
        3900,
        220,
        5,
        ("nuci verzi", "zahăr", "cuișoare"),
    ),
    ProductSeed(
        "Magiun de prune",
        "magiun-de-prune",
        "magiunuri",
        "Prune brumării fierte o zi întreagă la ceaun, fără zahăr. Gros, închis la culoare, ca odinioară.",
        2500,
        370,
        30,
        ("prune",),
    ),
    ProductSeed(
        "Magiun de mere cu scorțișoară",
        "magiun-de-mere-cu-scortisoara",
        "magiunuri",
        "Mere ionatan coapte și pasate, cu scorțișoară. Bun pe pâine prăjită sau în plăcintă.",
        2200,
        370,
        20,
        ("mere", "scorțișoară"),
    ),
    ProductSeed(
        "Gem de smochine cu nucă",
        "gem-de-smochine-cu-nuca",
        "editii-de-sezon",
        "Smochine coapte cu miez de nucă, făcut doar toamna, câteva zeci de borcane pe an.",
        4200,
        220,
        4,
        ("smochine", "zahăr", "nucă", "lămâie"),
    ),
    ProductSeed(
        "Gem de măceșe",
        "gem-de-macese",
        "editii-de-sezon",
        "Măceșe culese după prima brumă, curățate una câte una. Plin de vitamina C.",
        3600,
        220,
        0,
        ("măceșe", "zahăr"),
    ),
)
