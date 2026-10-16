"""Seed a deterministic, explicitly synthetic 1,000-item marketplace catalog."""

from dataclasses import dataclass
from itertools import product

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Product

PLACEHOLDER_IMAGE = "/images/demo-product-placeholder.svg"
IMAGE_DIRECTORY = "/images/products"
VARIANTS = (
    "Everyday",
    "Compact",
    "Lightweight",
    "Classic",
    "Modern",
    "Travel-ready",
    "Minimal",
    "Utility",
    "Soft-touch",
    "Durable",
)

IMAGE_RULES: dict[str, tuple[tuple[tuple[str, ...], str], ...]] = {
    "Electronics & Accessories": (
        (("headphone", "earphone", "earbud"), "headphones"),
        (("speaker",), "speaker"),
        (("keyboard",), "keyboard"),
        (("mouse",), "mouse"),
        (("laptop",), "laptop"),
        (("phone",), "smartphone"),
        (("tripod", "webcam"), "camera"),
        (("light",), "desk-light"),
        (("headphone carry case",), "headphones-product"),
        (("pouch", "carry case"), "bag"),
        (("cable", "hub", "adapter", "screen", "memory card"), "electronics-board"),
    ),
    "Electronics": (
        (("earbud", "earphone", "headphone"), "headphones"),
        (("phone",), "smartphone"),
    ),
    "Fashion & Footwear": (
        (("sneaker",), "sneakers"),
        (("shoe", "sandal", "flip-flop", "boot"), "shoes"),
        (("bag", "tote", "holder", "pouch"), "bag"),
        (("watch", "wristband"), "watch"),
        (("shirt", "kurta", "scarf", "beanie", "sock"), "shirt"),
        (("trouser", "jogger", "dress", "legging", "jacket", "waistcoat", "belt"), "fashion"),
    ),
    "Clothing": (
        (("kurta", "shirt", "dress", "trouser", "jacket"), "shirt"),
    ),
    "Home & Kitchen": (
        (("bottle",), "bottle"),
        (("mug",), "mug"),
        (("food", "lunch box", "cutting board", "produce", "measuring", "spatula", "spice"), "kitchen"),
        (("towel", "cushion", "basket", "cleaning cloth", "bedsheet", "laundry", "hanger"), "home"),
        (("planter", "night light"), "desk-light"),
        (("key holder", "drawer liner"), "interior"),
    ),
    "Beauty & Personal Care": (
        (("makeup", "cosmetic", "nail"), "cosmetics"),
        (("toiletry", "travel bottles", "face towel"), "beauty"),
        (("hair", "face", "facial", "skin", "body", "spa", "brush"), "skincare"),
    ),
    "Books & Stationery": (
        (("pencil", "pen", "sketchbook"), "art-supplies"),
        (("index card", "document folder", "page marker"), "books"),
        (("notebook", "journal", "planner", "graph"), "stationery"),
    ),
    "Sports, Toys & Lifestyle": (
        (("yoga", "seat pad"), "yoga"),
        (("resistance", "roller", "skipping", "exercise", "running armband"), "fitness"),
        (("bottle",), "bottle"),
        (("playing cards", "puzzle", "ball", "toy"), "toys"),
        (("daypack", "luggage organizer", "binocular case"), "bag"),
        (("picnic", "seat pad"), "home"),
    ),
}

CATEGORY_IMAGES = {
    "Electronics & Accessories": "electronics-board",
    "Electronics": "electronics-board",
    "Fashion & Footwear": "fashion",
    "Clothing": "shirt",
    "Home & Kitchen": "kitchen",
    "Beauty & Personal Care": "beauty",
    "Books & Stationery": "books",
    "Sports, Toys & Lifestyle": "fitness",
}


def product_image_path(name: str, category: str) -> str:
    normalized_name = name.casefold()
    for keywords, image_name in IMAGE_RULES.get(category, ()):
        if any(keyword in normalized_name for keyword in keywords):
            return f"{IMAGE_DIRECTORY}/{image_name}.jpg"
    fallback = CATEGORY_IMAGES.get(category)
    return f"{IMAGE_DIRECTORY}/{fallback}.jpg" if fallback else PLACEHOLDER_IMAGE


@dataclass(frozen=True)
class CategoryCatalog:
    category: str
    sku_prefix: str
    price_floor_rupees: int
    families: tuple[tuple[str, str], ...]


CATALOGS = (
    CategoryCatalog(
        "Electronics & Accessories",
        "ELEC",
        299,
        (
            ("USB-C Charging Cable", "braided cable for everyday device charging"),
            ("Wireless Mouse", "wireless pointing device for desk and travel use"),
            ("Bluetooth Speaker", "portable audio speaker for personal listening"),
            ("Laptop Sleeve", "padded protective sleeve for compatible laptops"),
            ("USB-C Hub", "multi-port connection hub for compatible devices"),
            ("Phone Stand", "adjustable stand for hands-free phone viewing"),
            ("Wired Earphones", "in-ear audio accessory with an inline microphone"),
            ("Power Bank Pouch", "protective storage pouch for portable chargers"),
            ("Keyboard Wrist Rest", "desk accessory designed to support a relaxed typing position"),
            ("Webcam Cover", "sliding privacy cover for compatible webcams"),
            ("HDMI Cable", "display cable for compatible screens and devices"),
            ("Tablet Stand", "adjustable tabletop stand for compatible tablets"),
            ("Cable Organizer Set", "reusable organizers for keeping desk cables together"),
            ("Screen Cleaning Kit", "soft cloth and cleaning accessories for device screens"),
            ("Laptop Riser", "ventilated angled riser for a desk setup"),
            ("Memory Card Case", "compact case for organizing compatible memory cards"),
            ("Universal Travel Adapter Pouch", "organizer pouch for travel charging accessories"),
            ("Headphone Carry Case", "protective case for storing compatible headphones"),
            ("Smartphone Tripod Mount", "adjustable mount for compatible phone tripods"),
            ("USB Desk Light", "compact adjustable light for a work surface"),
        ),
    ),
    CategoryCatalog(
        "Fashion & Footwear",
        "FASH",
        399,
        (
            ("Cotton Crew T-Shirt", "breathable cotton-blend crew-neck top for casual wear"),
            ("Everyday Polo Shirt", "collared short-sleeve shirt for casual outfits"),
            ("Casual Button Shirt", "versatile button-front shirt for everyday dressing"),
            ("Straight-Fit Trousers", "comfortable straight-cut trousers for daily use"),
            ("Relaxed Joggers", "soft casual trousers with an elasticated waist"),
            ("Canvas Slip-On Shoes", "light casual footwear with a flexible sole"),
            ("Lace-Up Walking Shoes", "cushioned everyday shoes for walking"),
            ("Low-Top Canvas Sneakers", "simple canvas sneakers for casual outfits"),
            ("Everyday Sandals", "open footwear with adjustable straps"),
            ("Ankle Socks Pack", "soft everyday socks for regular footwear"),
            ("Cotton Scarf", "lightweight scarf for layering and everyday styling"),
            ("Knit Beanie", "soft knit headwear for cool-weather outfits"),
            ("Adjustable Fabric Belt", "adjustable belt with a simple everyday design"),
            ("Compact Crossbody Bag", "hands-free bag with a practical everyday layout"),
            ("Canvas Tote Bag", "reusable carryall for daily essentials"),
            ("Slim Card Holder", "compact holder for organizing cards"),
            ("Lightweight Rain Jacket", "packable outer layer for light rainy conditions"),
            ("Cotton Kurta", "comfortable cotton-blend kurta for everyday wear"),
            ("A-Line Casual Dress", "easy-to-wear dress with a gently flared silhouette"),
            ("Stretch Leggings", "stretch fabric leggings for casual everyday outfits"),
            ("Denim-Style Shorts", "casual shorts with practical pockets"),
            ("Lightweight Waistcoat", "layering piece for smart-casual outfits"),
            ("Everyday Flip-Flops", "light slip-on footwear for relaxed use"),
            ("Lace-Up Ankle Boots", "ankle-height footwear with a practical lace-up fit"),
            ("Minimalist Wristband", "simple accessory for everyday styling"),
        ),
    ),
    CategoryCatalog(
        "Home & Kitchen",
        "HOME",
        199,
        (
            ("Insulated Water Bottle", "reusable bottle for carrying drinks on the go"),
            ("Ceramic Tea Mug", "everyday mug for serving hot or cold drinks"),
            ("Glass Food Storage Set", "reusable containers for storing prepared food"),
            ("Cotton Kitchen Towels", "absorbent towels for routine kitchen tasks"),
            ("Bamboo Cutting Board", "kitchen board for everyday food preparation"),
            ("Stainless Steel Lunch Box", "reusable container for packed meals"),
            ("Reusable Produce Bags", "washable bags for organizing fresh produce"),
            ("Measuring Spoon Set", "stackable measuring spoons for cooking and baking"),
            ("Silicone Spatula", "heat-resistant flexible spatula for kitchen preparation"),
            ("Cotton Cushion Cover", "removable cover for a standard decorative cushion"),
            ("Woven Storage Basket", "lightweight basket for household organization"),
            ("Microfiber Cleaning Cloths", "reusable cloths for household surface cleaning"),
            ("Tabletop Planter", "compact planter for indoor decorative plants"),
            ("Cotton Bedsheet Set", "soft bedding set for a standard-sized bed"),
            ("LED Night Light", "compact low-brightness light for indoor use"),
            ("Wall-Mount Key Holder", "entryway organizer for keeping keys together"),
            ("Non-Slip Drawer Liner", "cut-to-fit liner for household drawers"),
            ("Steel Spice Container Set", "lidded containers for organizing dry spices"),
            ("Laundry Storage Bag", "reusable bag for collecting household laundry"),
            ("Foldable Utility Hanger", "space-conscious hanger for household storage"),
        ),
    ),
    CategoryCatalog(
        "Beauty & Personal Care",
        "BEAU",
        149,
        (
            ("Reusable Makeup Pad Set", "washable pads for a reusable personal-care routine"),
            ("Wide-Tooth Hair Comb", "comb designed for gentle everyday hair grooming"),
            ("Travel Toiletry Pouch", "zippered pouch for organizing personal-care essentials"),
            ("Nail Care Tool Set", "basic tools for at-home nail grooming"),
            ("Soft Cotton Face Towels", "gentle reusable towels for everyday face care"),
            ("Manual Facial Cleansing Brush", "soft-bristle brush for personal cleansing routines"),
            ("Refillable Travel Bottles", "small reusable bottles for carrying toiletries"),
            ("Cosmetic Organizer Tray", "compact tray for organizing personal-care items"),
            ("Padded Spa Headband", "soft headband for keeping hair back during routines"),
            ("Gentle Body Brush", "everyday brush for personal grooming and bathing"),
        ),
    ),
    CategoryCatalog(
        "Books & Stationery",
        "BOOK",
        99,
        (
            ("Ruled Notebook", "paper notebook for notes, lists, and daily writing"),
            ("Dot Grid Journal", "dot-grid pages for journaling and planning"),
            ("Hardcover Sketchbook", "blank paper book for drawing and creative practice"),
            ("Weekly Planner", "dated-layout planner for organizing weekly tasks"),
            ("Graph Paper Pad", "squared paper pad for diagrams and calculations"),
            ("Index Card Set", "blank cards for study notes and quick reference"),
            ("Document Folder", "folder for keeping loose papers organized"),
            ("Mechanical Pencil Set", "refillable pencils for writing and drawing"),
            ("Fine-Line Pen Set", "assorted fine-line pens for notes and illustration"),
            ("Reusable Page Markers", "removable markers for locating pages and sections"),
        ),
    ),
    CategoryCatalog(
        "Sports, Toys & Lifestyle",
        "LIFE",
        249,
        (
            ("Yoga Exercise Mat", "cushioned mat for floor-based stretching and exercise"),
            ("Resistance Band Set", "elastic bands for a range of home exercise movements"),
            ("Stainless Steel Sports Bottle", "reusable bottle for carrying drinks during activities"),
            ("Foam Roller", "firm roller for self-guided stretching routines"),
            ("Skipping Rope", "adjustable rope for basic cardio workouts"),
            ("Compact Yoga Block", "support block for balance and stretching exercises"),
            ("Travel Playing Cards", "standard-size card deck for travel and home games"),
            ("Wooden Puzzle Set", "reusable wooden puzzles for hands-on leisure"),
            ("Soft Throw Ball", "lightweight ball for casual indoor or outdoor play"),
            ("Reusable Picnic Blanket", "foldable blanket for outdoor leisure"),
            ("Lightweight Daypack", "compact backpack for day trips and daily essentials"),
            ("Reflective Running Armband", "adjustable reflective band for outdoor visibility"),
            ("Compact Binocular Case", "protective case for storing compatible compact binoculars"),
            ("Foldable Water-Resistant Seat Pad", "portable pad for outdoor seating"),
            ("Travel Luggage Organizer Set", "reusable pouches for organizing packed belongings"),
        ),
    ),
)


def generate_demo_products() -> list[Product]:
    """Build stable product rows with the requested exact category distribution."""
    generated: list[Product] = []
    for catalog in CATALOGS:
        for index, (variant, (family, detail)) in enumerate(product(VARIANTS, catalog.families), start=1):
            price_rupees = catalog.price_floor_rupees + ((index * 137) % 8500)
            generated.append(
                Product(
                    name=f"{variant} {family}",
                    description=f"Demo catalog item. {detail.capitalize()}; {variant.lower()} style.",
                    category=catalog.category,
                    sku=f"DEMO-{catalog.sku_prefix}-{index:04d}",
                    price_paise=price_rupees * 100,
                    stock=5 + (index * 7) % 46,
                    image_url=product_image_path(f"{variant} {family}", catalog.category),
                    is_active=True,
                )
            )
    return generated


def seed_products(db: Session) -> tuple[int, int]:
    """Insert missing generated SKUs, preserving all existing product rows."""
    expected = generate_demo_products()
    expected_by_sku = {product.sku: product for product in expected}
    existing = db.scalars(select(Product).where(Product.sku.in_(expected_by_sku))).all()
    existing_by_sku = {product.sku: product for product in existing}

    for sku, product in expected_by_sku.items():
        if sku in existing_by_sku:
            current = existing_by_sku[sku]
            if current.name != product.name or current.category != product.category:
                raise ValueError(f"Existing product SKU conflicts with demo catalog: {sku}")
            current.image_url = product.image_url

    missing = [product for product in expected if product.sku not in existing_by_sku]
    db.add_all(missing)
    unpictured_products = db.scalars(
        select(Product).where(
            Product.sku.not_in(expected_by_sku),
            Product.image_url.in_(("", PLACEHOLDER_IMAGE)),
        )
    ).all()
    for product in unpictured_products:
        product.image_url = product_image_path(product.name, product.category)
    db.flush()
    return len(missing), len(existing_by_sku)


def main() -> None:
    with SessionLocal.begin() as db:
        inserted, already_present = seed_products(db)
        products = db.scalars(select(Product)).all()
        pictured = sum(product.image_url.startswith(f"{IMAGE_DIRECTORY}/") for product in products)
    print(
        f"Demo catalog seeding complete: inserted {inserted}; "
        f"already present {already_present}; target {len(generate_demo_products())}."
    )
    print(f"Products using local product photos: {pictured}/{len(products)}.")
    if pictured != len(products):
        print(f"Some products still need image mapping; placeholder asset: {PLACEHOLDER_IMAGE}")


if __name__ == "__main__":
    main()
