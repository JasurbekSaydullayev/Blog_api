from pydantic import BaseModel


class UserBase(BaseModel):
    username: str
    first_name: str
    last_name: str
    email: str


class UserCreate(UserBase):
    password: str


class UserUpdate(UserBase):
    pass


class BlogBase(BaseModel):
    title: str
    description: str
    owner_name: str
    tags: [str] = None


class BlogView(BlogBase):
    id: int
    created_at: str
    updated_at: str
    views: int


class BlogCreate(BlogBase):
    pass


class BlogUpdate(BlogBase):
    pass


class CommentBase(BaseModel):
    username: str
    blog_id: int
    content: str


class CommentCreate(CommentBase):
    pass


class CommentUpdate(CommentBase):
    pass


class CommentView(CommentBase):
    id: int
    created_at: str
    updated_at: str




