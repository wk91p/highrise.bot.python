from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Sequence, Literal
from enum import Enum, unique

SortOptions = Literal["desc", "asc"]

@unique
class ItemCategory(str, Enum):
    BAG = "bag"
    BLUSH = "blush"
    BODY = "body"
    DRESS = "dress"
    EARRINGS = "earrings"
    EMOTE = "emote"
    EYE = "eye"
    EYEBROW = "eyebrow"
    FACE_HAIR = "face_hair"
    FISHING_ROD = "fishing_rod"
    FRECKLE = "freckle"
    GLASSES = "glasses"
    GLOVES = "gloves"
    HAIR_BACK = "hair_back"
    HAIR_FRONT = "hair_front"
    HANDBAG = "handbag"
    HAT = "hat"
    JACKET = "jacket"
    LASHES = "lashes"
    MOLE = "mole"
    MOUTH = "mouth"
    NECKLACE = "necklace"
    NOSE = "nose"
    PANTS = "pants"
    SHIRT = "shirt"
    SHOES = "shoes"
    SHORTS = "shorts"
    SKIRT = "skirt"
    WATCH = "watch"
    FULLSUIT = "fullsuit"
    SOCK = "sock"
    TATTOO = "tattoo"
    ROD = "rod"
    AURA = "aura"

@unique
class Rarity(str, Enum):
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"
    MYTHICAL = 'mythical'
    NONE = "none_"

@unique
class LegacyRewardCategory(str, Enum):
    POPS = "pops"
    GEMS = "gems"
    OUTFIT = "outfit"
    GACHA_TOKENS = "gacha_tokens"
    FURNITURE = "furniture"
    COLLECTIBLE = "collectible"
    LUCKY_TOKENS = "lucky_tokens"
    EVENT_TICKETS = "event_tickets"
    EMOTE = "emote"
    GIFT_BOX = "gift_box"
    ENERGY = "energy"
    VIP_DAYS = "vip_days"
    CHIPS = "chips"
    PROMO_TOKENS = "promo_tokens"
    SKYPASS_STARS = "skypass_stars"
    ROOM_BOOST_TOKENS = "room_boost_tokens"
    ROOM_VOICE_TOKENS = "room_voice_tokens"
    POCKET_COINS = "pocket_coins"
    CASH = "cash"
    CUSTOM_CURRENCY = "custom_currency"
    PET = "pet"

@unique
class NFIStrategy(str, Enum):
    SEQUENTIAL = "sequential"
    TOTAL_DEFINED = "total_defined"
    POOL = "pool"


@dataclass(frozen=True)
class WebOutfitItemColors:
    """Color/palette data for a single web-API outfit item."""
    dependent_colors: Sequence[str] = field(default_factory=tuple)
    palettes: Sequence[list] = field(default_factory=tuple)
    linked_colors: str = ""

@dataclass(frozen=True)
class WebOutfitItem:
    """A single outfit item as returned by the public web API.
    Distinct shape from the WebSocket API's OutfitItem."""
    item_id: str
    name: str
    rarity: str
    active_palette: int
    parts: list[tuple[str, str]]
    colors: Optional[WebOutfitItemColors] = None

@dataclass(frozen=True)
class ActiveRoomInfo:
    """The room a user is currently active in, if any."""
    id: str
    display_name: str
    code_name: Optional[str]

@dataclass(frozen=True)
class Crew:
    """A user's crew."""
    id: str
    name: str

@dataclass(frozen=True)
class PublicUser:
    """A user's public profile, as returned by `GET /users/{user_id}`."""
    user_id: str
    username: str
    bio: str
    joined_at: datetime
    last_online_in: Optional[datetime]
    num_followers: int
    num_following: int
    num_friends: int
    active_room: Optional[ActiveRoomInfo]
    country_code: str
    crew: Optional[Crew]
    voice_enabled: bool
    discord_id: Optional[str] = None
    outfit: list[WebOutfitItem] = field(default_factory=list)

@dataclass(frozen=True)
class PublicRoomBasic:
    """A lighter room shape, as returned by `GET /rooms` (list endpoint)."""
    room_id: str
    disp_name: str
    created_at: Optional[datetime]
    access_policy: str
    category: str
    owner_id: str
    description: str
    is_home_room: bool | None = None
    locale: list[str] = field(default_factory=list)
    designer_ids: list[str] = field(default_factory=list)
    moderator_ids: list[str] = field(default_factory=list)

@dataclass(frozen=True)
class PublicRoom(PublicRoomBasic):
    """A room's public data, as returned by `GET /rooms/{room_id}`"""
    num_connected: int = 0
    crew_id: str | None = None
    bots: str | None = None
    indicators: str | None = None
    thumbnail_url: str | None = None
    banner_url: str | None = None

@dataclass(frozen=True)
class PostItem:
    """ Single post item """
    item_id: str
    active_palette: int = 0
    account_bound: bool = False

@dataclass(frozen=True)
class PostInventory:
    items: list[PostItem] = field(default_factory=list)

@dataclass(frozen=True)
class PostBody:
    text: str
    inventory: PostInventory

@dataclass(frozen=True)
class Comment:
    """ Single post comment """
    id: str
    content: str
    post_id: str
    author_id: str
    author_name: str
    num_likes: int

@dataclass(frozen=True)
class PublicPostBasic:
    """ A lighter post shape, as returned by `GET /post` (list endpoint)"""
    post_id: str
    author_id: str | None = None
    created_at: str | None = None
    file_key: str | None = None
    type: str | None = None
    visibility: str = "private"
    num_comments: int = 0
    num_likes: int = 0
    num_reposts: int = 0
    body: PostBody | None = None
    caption: str | None = None
    featured_user_ids: list[str] = field(default_factory=list)

@dataclass(frozen=True)
class PublicPost(PublicPostBasic):
    """A post's public data, as returned by `GET /post/{post_id}`"""
    comments: list[Comment] = field(default_factory=list)

@dataclass(frozen=True)
class SkinPart:
    """A single skin part attachment on an item."""
    bone: str
    slot: str
    image_file: str
    attachment_name: Optional[str] = None
    has_remote_render_layer: Optional[bool] = None

@dataclass(frozen=True)
class ItemBasic:
    """A single item, as returned by `GET /items/search`."""
    item_id: str
    item_name: str
    category: Optional[ItemCategory] = None
    color_linked_categories: list[str] = field(default_factory=list)
    color_palettes: list[str] = field(default_factory=list)
    created_at: Optional[datetime] = None
    description_key: Optional[str] = None
    gems_sale_price: Optional[int] = None
    inspired_by: list[str] = field(default_factory=list)
    is_purchasable: bool = False
    is_tradable: bool = False
    image_url: Optional[str] = None
    icon_url: Optional[str] = None
    link_ids: list[str] = field(default_factory=list)
    m_dependent_colors: list[tuple[ItemCategory, int, int]] = field(default_factory=list)
    m_front_skin_part_list: list[SkinPart] = field(default_factory=list)
    m_back_skin_part_list: list[SkinPart] = field(default_factory=list)
    m_hidden_skin_parts: set = field(default_factory=set)
    pops_sale_price: Optional[int] = None
    rarity: Rarity = Rarity.NONE
    release_date: Optional[datetime] = None

@dataclass(frozen=True)
class Item(ItemBasic):
    """A full item, as returned by `GET /items/{item_id}`."""
    acquisition_cost: Optional[int] = None
    acquisition_amount: Optional[int] = None
    acquisition_currency: Optional[str] = None

@dataclass(frozen=True)
class Affiliation:
    id: str
    title: str
    type: str
    event_type: Optional[str] = None

@dataclass(frozen=True)
class RelatedItem:
    item_id: str
    disp_name: str
    rarity: Rarity = Rarity.NONE

@dataclass(frozen=True)
class RelatedItems:
    affiliations: list[Affiliation] = field(default_factory=list)
    items: list[RelatedItem] = field(default_factory=list)

@dataclass(frozen=True)
class Seller:
    user_id: str
    username: str
    outfit: list[WebOutfitItem] = field(default_factory=list)
    last_connected_at: Optional[datetime] = None

@dataclass(frozen=True)
class StorefrontListings:
    sellers: list[Seller] = field(default_factory=list)
    pages: int = 0
    total: int = 0

class NFIStrategy(str, Enum):
    SEQUENTIAL = "sequential"
    TOTAL_DEFINED = "total_defined"
    POOL = "pool"


@dataclass(frozen=True)
class NFIItemMetadata:
    item_number: int
    stack_id: str


@dataclass(frozen=True)
class NFITemplateMetadata:
    strategy: NFIStrategy
    total_amount: Optional[int] = None


@dataclass(frozen=True)
class ItemMetadata:
    nfi_metadata: Optional[NFIItemMetadata] = None
    nfi_template_metadata: Optional[NFITemplateMetadata] = None


@dataclass(frozen=True)
class Reward:
    category: LegacyRewardCategory
    amount: int
    reward_id: str = ""
    item_id: Optional[str] = None
    account_bound: bool = False
    metadata: Optional[ItemMetadata] = None


@dataclass(frozen=True)
class LimitedKompuReward:
    expires_at: Optional[datetime] = None
    rewards: list[Reward] = field(default_factory=list)


@dataclass(frozen=True)
class ProgressReward:
    rewards_at: int
    rewards: list[Reward] = field(default_factory=list)


@dataclass(frozen=True)
class Grab:
    grab_id: str
    title: str
    description: str
    background_color: tuple[int, int, int]
    banner_img_url: str
    starts_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    rewards: list[Reward] = field(default_factory=list)
    primary_img_url: Optional[str] = None
    secondary_img_url: Optional[str] = None
    costs: list[Reward] = field(default_factory=list)
    kompu_rewards: list[Reward] = field(default_factory=list)
    is_tradable: bool = True
    limited_time_kompu: Optional[LimitedKompuReward] = None
    progress_reward: Optional[ProgressReward] = None