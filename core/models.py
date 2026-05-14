from django.db import models


class Requester(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    location = models.CharField(max_length=255)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    class Meta:
        ordering = ['name']
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'phone', 'location'],
                name='unique_requester_identity',
            ),
        ]

    def __str__(self):
        return self.name


class EmergencyType(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_assigned_teams(self):
        """Get teams automatically assigned to this emergency type"""
        # Mapping of emergency type names to team names
        type_to_teams = {
            'medical': ['Ambulance Team'],
            'fire': ['Firefighters'],
            'robbery': ['Police Department'],
            'robbery / police': ['Police Department'],
            'police': ['Police Department'],
            'accident': ['Emergency Rescue'],
            'power outage': ['Electricity Maintenance'],
            'power': ['Electricity Maintenance'],
            'hazard': ['Civil Protection'],
            'infrastructure': ['Civil Protection'],
        }
        
        # Get matching teams for this emergency type
        type_name = self.name.lower()
        matching_teams = type_to_teams.get(type_name, [])
        
        if matching_teams:
            return ResponseTeam.objects.filter(name__in=matching_teams)
        
        return ResponseTeam.objects.none()


class EmergencyRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=255)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    before_image = models.ImageField(upload_to='emergency_requests/before/', blank=True, null=True)
    after_image = models.ImageField(upload_to='emergency_requests/after/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    requester = models.ForeignKey(
        Requester,
        on_delete=models.PROTECT,
        related_name='emergency_requests',
    )
    emergency_type = models.ForeignKey(
        EmergencyType,
        on_delete=models.PROTECT,
        related_name='emergency_requests',
    )

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return self.title

    @property
    def emergency_type_key(self):
        return self.emergency_type.name.lower().replace(' ', '_')


class ResponseTeam(models.Model):
    name = models.CharField(max_length=100)
    contact = models.CharField(max_length=100)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Assignment(models.Model):
    emergency_request = models.ForeignKey(
        EmergencyRequest,
        on_delete=models.CASCADE,
        related_name='assignments',
    )
    response_team = models.ForeignKey(
        ResponseTeam,
        on_delete=models.PROTECT,
        related_name='assignments',
    )
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-assigned_at']
        constraints = [
            models.UniqueConstraint(
                fields=['emergency_request', 'response_team'],
                name='unique_request_team_assignment',
            ),
        ]

    def __str__(self):
        return f'{self.response_team} assigned to {self.emergency_request}'
