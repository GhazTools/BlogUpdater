"""
file_name = vault_reader.py
Created On: 2024/07/09
Lasted Updated: 2024/07/09
Description: _FILL OUT HERE_
Edit Log:
2024/07/09
    - Created file
"""

# STANDARD LIBRARY IMPORTS
from pathlib import Path
from typing import Final

# THIRD PARTY LIBRARY IMPORTS

# LOCAL LIBRARY IMPORTS
from src.database.repositories.image_repository import ImageRepository
from src.database.repositories.blog_post_repository import BlogPostRepository

from src.models.image_model import ImageModel
from src.models.blog_post_model import BlogPostModel

from src.utils.environment import Environment, EnvironmentVariableKeys

Images = list[ImageModel]
BlogPosts = list[BlogPostModel]


class VaultReader:
    """
    A class for reading an obsidian vault to manage blog posts
    """

    VAULT_PATH: Final[str] = Environment.get_environment_variable(
        EnvironmentVariableKeys.VAULT_PATH
    )
    IGNORE_FOLDERS: Final[list[str]] = [".git", ".obsidian"]

    def __init__(self: "VaultReader") -> None:
        image_data: tuple[Images, Images] = self._extract_image_data()
        self._images = image_data[0]
        self._images_to_add = image_data[1]

        blog_post_data: tuple[BlogPosts, BlogPosts] = self._extract_blog_posts_data()
        self._blog_posts = blog_post_data[0]
        self._blog_posts_to_add = blog_post_data[1]

    @property
    def images(self: "VaultReader") -> Images:
        """
        Return all images in the vault
        """
        return self._images

    @property
    def images_to_add(self: "VaultReader") -> Images:
        """
        Returns a list of images that are not in the database=
        """

        return self._images_to_add

    @property
    def blog_posts(self: "VaultReader") -> BlogPosts:
        """
        Return all blog posts in the vault
        """
        return self._blog_posts

    @property
    def blog_posts_to_add(self: "VaultReader") -> BlogPosts:
        """
        Returns a list of blog posts that are not in the database
        """

        return self._blog_posts_to_add

    def reload_vault_reader(self: "VaultReader") -> None:
        """
        Reloads the vault reader
        """

        image_data: tuple[Images, Images] = self._extract_image_data()
        self._images = image_data[0]
        self._images_to_add = image_data[1]

        blog_post_data: tuple[BlogPosts, BlogPosts] = self._extract_blog_posts_data()
        self._blog_posts = blog_post_data[0]
        self._blog_posts_to_add = blog_post_data[1]

    # PRIVATE METHODS START HERE

    def _extract_image_data(self: "VaultReader") -> tuple[Images, Images]:
        """
        Extracts all images from the vault

        The first list is all images, and the second is images that need to be added to the database
        """

        image_dir_path: Path = Path(self.VAULT_PATH) / "__IMAGES__"
        images: Images = []
        images_to_add: Images = []

        for object_path in image_dir_path.iterdir():
            if not self._validate_image_path(object_path):
                continue

            with ImageRepository() as repository:
                with open(object_path, "rb") as image_file:
                    image_name: str = object_path.name
                    image_data: bytes = image_file.read()

                    image_in_db = repository.check_if_exists(image_name)
                    released = image_in_db and repository.check_if_released(image_name)

                    image: ImageModel = ImageModel(
                        image_name=image_name, image_data=image_data, released=released
                    )

                    images.append(image)

                    if not image_in_db:
                        images_to_add.append(image)

        return (images, images_to_add)

    def _validate_image_path(self, object_path: Path) -> bool:
        """
        Validates that the image path is a valid image
        """

        # TODO: Currently only supports png

        if not object_path.is_file():
            return False

        if not object_path.name.endswith(".png"):
            return False

        return True

    def _extract_blog_posts_data(self: "VaultReader") -> tuple[BlogPosts, BlogPosts]:
        """
        Extracts all blog posts from the vault
        """

        image_dir_path: Path = Path(self.VAULT_PATH) / "__BLOG_POSTS__"
        blog_posts: BlogPosts = []
        blog_posts_to_add: BlogPosts = []

        with BlogPostRepository() as repository:
            for object_path in image_dir_path.iterdir():
                # Each blog post is a directory
                if object_path.is_file():
                    continue

                post_name: str = object_path.name
                description: str = self._get_post_description(object_path)
                text: str = self._get_post_text(object_path)

                post_in_db = repository.check_if_exists(post_name)
                released = post_in_db and repository.check_if_released(post_name)

                blog_post: BlogPostModel = BlogPostModel(
                    post_name=post_name,
                    description=description,
                    text=text,
                    released=released,
                    release_date=None,
                    last_updated=None,
                )

                blog_posts.append(blog_post)

                if not post_in_db:
                    blog_posts_to_add.append(blog_post)

        return (blog_posts, blog_posts_to_add)

    def _get_post_description(self: "VaultReader", post_path: Path) -> str:
        """
        Extracts the description of a blog post
        """

        description_path: Path = post_path / "description.md"

        if not description_path.exists():
            raise ValueError(f"Description file for {post_path.name} does not exist")

        with open(description_path, "r", encoding="UTF-8") as description_file:
            description: str = description_file.read()

        if len(description) > 50:
            raise ValueError(
                f"Description for {post_path.name} is too long, max length is 50 characters"
            )

        return description

    def _get_post_text(self: "VaultReader", post_path: Path) -> str:
        """
        Extracts the text of a blog post
        """

        text_path: Path = post_path / "text.md"

        if not text_path.exists():
            raise ValueError(f"Text file for {post_path.name} does not exist")

        with open(text_path, "r", encoding="UTF-8") as text_file:
            text: str = text_file.read()

        return text

    # PRIVATE METHODS END HERE
