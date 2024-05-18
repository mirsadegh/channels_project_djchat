from rest_framework import viewsets  
from .models import Server 
from .serializer import ServerSerializer  
from rest_framework.response import Response  
from rest_framework.exceptions import ValidationError, AuthenticationFailed 
from django.db.models import Count  
from .schema import server_list_docs


class ServerListViewSet(viewsets.ViewSet):
    queryset = Server.objects.all()  

    @server_list_docs
    def list(self, request):
        """
            Processes the list request based on query parameters.

            Args:
            request: The HTTP request object containing query parameters.

            Raises:
            AuthenticationFailed: If the user is not authenticated for specific queries.
            ValidationError: If there is an issue with the provided server ID.

            Returns:
            Response: A response containing the serialized data based on the query parameters.
        """

        # Extracting query parameters from the request
        category = request.query_params.get("category")
        qty = request.query_params.get("qty")
        by_user = request.query_params.get("by_user") == "true"
        by_serverid = request.query_params.get("by_serverid")
        with_num_members = request.query_params.get("with_num_members") == "true"


        # Filtering the queryset based on the category if provided
        if category:
            self.queryset = self.queryset.filter(category__name=category)

        # Filtering the queryset based on the requesting user if requested
        if by_user:
            if by_user and request.user.is_authenticated:
                user_id = request.user.id
                self.queryset = self.queryset.filter(member=user_id)
            else:
                raise AuthenticationFailed()    

        # Annotating the queryset with the count of members if requested
        if with_num_members:
            self.queryset = self.queryset.annotate(num_members=Count("member"))

        # Limiting the queryset results to a specified quantity if provided
        if qty:
            self.queryset = self.queryset[:int(qty)]

        # Filtering the queryset based on server ID if provided
        if by_serverid:
            try:
                self.queryset = self.queryset.filter(id=by_serverid)
                if not self.queryset.exists():
                    raise ValidationError(detail=f"Server with id {by_serverid} not found")
            except ValueError:
                raise ValidationError(detail=f"Server value error")

        # Serializing the queryset and returning the response
        serializer = ServerSerializer(self.queryset, many=True, context={"num_members": with_num_members})
        return Response(serializer.data)
