from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter
from tool.utils.calc_ab import analysis_function
from tool.utils.calc_cont import cont_calculations
from tool.utils.calc_prop import prop_calculations
from .models import Test
from .serializers import TestSerializer

class TestViewSet(viewsets.ModelViewSet):
    queryset = Test.objects.all()
    serializer_class = TestSerializer
    filter_backends = [SearchFilter]
    search_fields = ['name', 'description']
    
    def get_queryset(self):
        return Test.objects.filter(user=self.request.user).order_by('-created_date')
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=["post"], permission_classes=[permissions.AllowAny])
    def calc_continuous_metric(self, request):
        # Extracting payload from request
        payload = request.data
        
        try:
            confidence_level = float(payload.get('confidence_level'))
            power = float(payload.get('power'))
            baseline_kpi = float(payload.get('baseline_kpi'))
            standard_deviation = float(payload.get('kpi_sd'))
            mde = float(payload.get('mde'))
            absolute = payload.get('absolute', True) in [True, 'true', 'True', 1, '1']
            arms = int(payload.get('arms'))
            daily_interactions = int(payload.get('daily_interactions'))
            two_tailed = payload.get('two_tailed', True) in [True, 'true', 'True', 1, '1']
            equal_allocation = payload.get('equal_allocation', True) in [True, 'true', 'True', 1, '1']

            revenue_per_conversion = payload.get('revenue_per_conversion', None)
            expected_uplift = payload.get('expected_uplift', None)
            allocations = payload.get('allocations', {})

        except ValueError as e:
            return Response({"error": "Invalid input types", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    

        # Call cont_calculations function
        try:
            results = cont_calculations(
                confidence_level, power, baseline_kpi, standard_deviation, mde,
                absolute, arms, daily_interactions, two_tailed, equal_allocation,
                revenue_per_conversion, expected_uplift, allocations
            )

        except Exception as e:
            return Response({"error": "Calculation error", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        # Return results
        return Response(results, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], permission_classes=[permissions.AllowAny])
    def calc_proportional_metric(self, request):
        # Extracting payload from request
        payload = request.data

        try:
            confidence_level = float(payload.get('confidence_level'))
            power = float(payload.get('power'))
            baseline_cr = float(payload.get('baseline_conversion_rate'))
            mde = float(payload.get('mde'))
            absolute = payload.get('absolute', True) in [True, 'true', 'True', 1, '1']
            arms = int(payload.get('arms'))
            daily_interactions = int(payload.get('daily_interactions'))
            two_tailed = payload.get('two_tailed_test', True) in [True, 'true', 'True', 1, '1']
            equal_allocation = payload.get('equal_allocation', True) in [True, 'true', 'True', 1, '1']
            revenue_per_conversion = payload.get('revenue_per_conversion')
            expected_uplift = payload.get('expected_uplift')
            allocations = payload.get('allocations', [])

        except ValueError as e:
            return Response({"error": "Invalid input types", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # Call prop_calculations function
        try:
            results = prop_calculations(
                confidence_level, power, baseline_cr, mde,
                absolute, arms, daily_interactions, two_tailed,
                equal_allocation, revenue_per_conversion, expected_uplift, allocations
            )

        except Exception as e:
            return Response({"error": "Calculation error", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # Return results
        return Response(results, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=["post"], permission_classes=[permissions.AllowAny])
    def calc_ab_metric(self, request):
        payload = request.data
        try:
            visitors_input = payload.get('visitors_input')
            conversions_input = payload.get('conversions_input')
            confidence_level = float(payload.get('confidence_level'))
            tail = payload.get('tail', 'two-tailed')

            # Ensure visitors_input and conversions_input are properly formatted dictionaries
            if not isinstance(visitors_input, dict) or not isinstance(conversions_input, dict):
                raise ValueError("Invalid input format for visitors or conversions data.")

            results = analysis_function(visitors_input, conversions_input, confidence_level, tail)
            return Response(results, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": "Error processing request", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        