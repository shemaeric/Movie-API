import graphene
from graphene_django.types import DjangoObjectType, ObjectType
from movies.models import Actor, Movies

# create a CraphicQL type for the actor model
class ActorType(DjangoObjectType):
    class Meta:
        model = Actor

# Create a GraphQL type for the movie model
class MovieType(DjangoObjectType):
    class Meta:
        model = Movies

# Create a Query Type
class Query(ObjectType):
    actor = graphene.Field(ActorType, id=graphene.Int())
    movie = graphene.Field(MovieType, id=graphene.Int())
    actors = graphene.List(ActorType)
    movies= graphene.List(MovieType)

    def resolve_actor(self, info, **kwargs):
        id = kwargs.get('id')

        if id is not None:
            return Actor.objects.get(pk=id)

        return None

    def resolve_movie(self, info, **kwargs):
        id = kwargs.get('id')

        if id is not None:
            return Movies.objects.get(pk=id)

        return None

    def resolve_actors(self, info, **kwargs):
        return Actor.objects.all()

    def resolve_movies(self, info, **kwargs):
        return Movies.objects.all()

# Create Input Object Types
class ActorInput(graphene.InputObjectType):
    id = graphene.ID()
    name = graphene.String()

class MoviesInput(graphene.InputObjectType):
    id = graphene.ID()
    title = graphene.String()
    actors = graphene.List(ActorInput)
    year = graphene.Int()

# Create mutation for actors
class CreateActor(graphene.Mutation):
    class Arguments:
        input = ActorInput(required= True)
    
    ok = graphene.Boolean()
    actor = graphene.Field(ActorType)

    @staticmethod
    def mutate(root, info, input=None):
        ok = True
        actor_instance = Actor(name=input.name)
        actor_instance.save()
        return CreateActor(ok=ok, actor=actor_instance)

class UpdateActor(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required= True)
        input = ActorInput(required=True)

    ok = graphene.Boolean()
    actor = graphene.Field(ActorType)

    @staticmethod
    def mutate(root, info, id, input=None):
        ok = False
        actor_instance = Actor.objects.get(pk=id)

        if actor_instance:
            ok = True
            actor_instance.name = input.name
            actor_instance.save()
            return UpdateActor(ok=ok, actor=actor_instance)
        return UpdateActor(ok=ok, actor=None)

# Create mutation for movies
class CreateMovie(graphene.Mutation):
    class Arguments:
        input = MoviesInput(required=True)

    ok = graphene.Boolean()
    movie = graphene.Field(MovieType)

    @staticmethod
    def mutate(root, info, input=None):
        ok = True
        actors = []
        for actor_input in input.actors:
            actor = Actor.objects.get(pk=actor_input.id)
            if(actor is None):
                return CreateActor(ok=False, movie=None)
            actors.append(actor)

        movie_instance = Movies(
            title = input.title,
            year = input.year
        )

        movie_instance.save()
        movie_instance.actors.set(actors)
        return CreateMovie(ok=ok, movie=movie_instance)

class UpdateMovie(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        input = MoviesInput(required=True)
    ok = graphene.Boolean()
    movie = graphene.Field(MovieType)

    @staticmethod
    def mutate(root, info, id, input=None):
        ok = False
        movie_instance = Movies.objects.get(pk=id)

        if movie_instance:
            ok = True
            actors = []
            for actor_input in input.actors:
                actor = Actor.objects.get(pk=actor_input.id)
                if actor is None:
                    return UpdateMovie(ok=False, movie=None)
                actors.append(actor)
            movie_instance.title = input.title
            movie_instance.year=input.year.save()
            movie_instance.actors.set(actors)
            return UpdateMovie(ok=ok, movie=movie_instance)
        return UpdateMovie(ok=ok, movie=None)

class Mutation(graphene.ObjectType):
    create_ctor = CreateActor.Field()
    update_actor = UpdateActor.Field()
    create_movie = CreateMovie.Field()
    update_movie = UpdateMovie.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)