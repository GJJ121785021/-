from django.contrib.auth.models import User
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import mixins, viewsets, filters

from rest_framework import generics, permissions
from rest_framework.reverse import reverse
from rest_framework.throttling import UserRateThrottle

from first_app.models import Snippet
from rest_framework import renderers
from first_app.permissions import IsOwnerOrReadOnly
from first_app.serializers import SnippetSerializer, UserSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, action, throttle_classes

from first_app.throttles import OncePerDayUserThrottle


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    This viewset automatically provides `list` and `detail` actions.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    throttle_classes = [UserRateThrottle]


class SnippetViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.

    Additionally we also provide an extra `highlight` action.
    """
    # 声明一个queryset
    queryset = Snippet.objects.all()

    # 序列化器
    serializer_class = SnippetSerializer

    # 权限
    permission_classes = [permissions.IsAuthenticatedOrReadOnly,
                          IsOwnerOrReadOnly]
    # 限流
    throttle_classes = [UserRateThrottle]

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

    # 在snippet列表页面 可加参数?title=xxx这样来精确查询，精确匹配title为xxx的对象
    # 在filterset_fields中添加了的字段才可查找
    # 可以通过双下划线 __  的方式来关联查找 ,前提是添加到 [] 里并且是有效的，
    # 另外可自行构建自己想要的字段 https://django-filter.readthedocs.io/en/latest/guide/rest_framework.html
    # (基于上面这个重写FilterSet=> 请注意，不支持将filterset_fieldsand filterset_class一起使用。)
    filterset_fields = ['title', 'owner__username']

    # 在snippet列表页面 可加参数?search=xxx这样来模糊查询，配置的code是选择能查询的字段，
    # 查询时不需要指定字段，只需要指定你要查找的内容，它会自动在所有添加在search_fields=[] 中的字段中查找
    # 比如 search_fields = ['code']    url?search=ccc  只会查找出（对象的）code字段包含有ccc的 对象（s）出来
    # search_fields = ['code', 'language']   会在对象的 code, language 这两个字段中查找
    # 注意 字段只能选择在Model中存在的（包括模型自建id）
    search_fields = ['code']

    # 在snippet列表页面 可加参数?ordering=filed_name 这样来进行排序,
    # 比如 ?ordering=id 根据id的正向排序（由低到高） ?ordering=-id是逆向排序
    # ?ordering=language,-id 先根据language正排，再根据id反排
    # 注意 字段只能选择在Model中存在的（包括模型自建id）
    ordring_fields = ['id', 'language']


    # def get_queryset(self):
    #     owner = self.request.query_params.get('owner', None)
    #     if owner is not None:
    #         return Snippet.objects.filter(owner__in=User.objects.filter(username=owner))
    #     return Snippet.objects.all()

    @action(detail=True, renderer_classes=[renderers.StaticHTMLRenderer])
    def highlight(self, request, *args, **kwargs):
        snippet = self.get_object()
        return Response(snippet.highlighted)

    @action(detail=False)
    def test(self, request, *args, **kwargs):
        s = {'a': 1, 'r': 223}
        return Response(s)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


@api_view(['GET'])
@throttle_classes([OncePerDayUserThrottle])
def api_root(request, format=None):
    return Response({
        'users': reverse('first_app:user-list', request=request, format=format),
        'snippets': reverse('first_app:snippet-list', request=request, format=format)
    })



# class SnippetList(generics.ListCreateAPIView):
#     queryset = Snippet.objects.all()
#     serializer_class = SnippetSerializer
#     permission_classes = [permissions.IsAuthenticatedOrReadOnly]
#
#     def perform_create(self, serializer):
#         serializer.save(owner=self.request.user)
#
#
# class SnippetDetail(generics.RetrieveUpdateDestroyAPIView):
#     queryset = Snippet.objects.all()
#     serializer_class = SnippetSerializer
#     permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
#
#
# class UserList(generics.ListAPIView):
#     queryset = User.objects.all()
#     serializer_class = UserSerializer
#
#
# class UserDetail(generics.RetrieveAPIView):
#     queryset = User.objects.all()
#     serializer_class = UserSerializer
#
#
#
#
# class SnippetHighlight(generics.GenericAPIView):
#     queryset = Snippet.objects.all()
#     renderer_classes = [renderers.StaticHTMLRenderer]
#
#     def get(self, request, *args, **kwargs):
#         snippet = self.get_object()
#         return Response(snippet.highlighted)
















# @api_view(['GET', 'POST'])
# def snippet_list(request, format=None):
#     """
#     List all code snippets, or create a new snippet.
#     """
#     if request.method == 'GET':
#         snippets = Snippet.objects.all()
#         serializer = SnippetSerializer(snippets, many=True)
#         return Response(serializer.data)
#         # return JsonResponse(serializer.data, safe=False)
#
#     elif request.method == 'POST':
#         serializer = SnippetSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#
# @api_view(['GET', 'PUT', 'DELETE'])
# def snippet_detail(request, pk, format=None):
#     """
#     Retrieve, update or delete a code snippet.
#     """
#     try:
#         snippet = Snippet.objects.get(pk=pk)
#     except Snippet.DoesNotExist:
#         return Response(status=status.HTTP_404_NOT_FOUND)
#
#     if request.method == 'GET':
#         serializer = SnippetSerializer(snippet)
#         return Response(serializer.data)
#
#     elif request.method == 'PUT':
#         serializer = SnippetSerializer(request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#     elif request.method == 'DELETE':
#         snippet.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)
