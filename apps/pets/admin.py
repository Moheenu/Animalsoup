from django.contrib import admin
from .models import Pet, PetHealthRecord

class PetHealthRecordInline(admin.TabularInline):
    model = PetHealthRecord
    extra = 1

@admin.register(Pet)
class PetAdmin(admin.ModelAdmin):
    list_display = ('name', 'pet_id', 'species', 'breed', 'owner', 'age_display', 'is_active')
    list_filter = ('species', 'gender', 'is_active', 'created_at')
    search_fields = ('name', 'pet_id', 'breed', 'owner__username', 'microchip_number')
    readonly_fields = ('pet_id', 'qr_code', 'created_at', 'updated_at')
    inlines = [PetHealthRecordInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('pet_id', 'owner', 'name', 'species', 'breed', 'gender')
        }),
        ('Physical Attributes', {
            'fields': ('date_of_birth', 'color', 'weight', 'microchip_number', 'blood_group')
        }),
        ('Medical Information', {
            'fields': ('allergies', 'medical_conditions', 'emergency_notes')
        }),
        ('Media', {
            'fields': ('photo', 'qr_code')
        }),
        ('Status', {
            'fields': ('is_active', 'created_at', 'updated_at')
        }),
    )

@admin.register(PetHealthRecord)
class PetHealthRecordAdmin(admin.ModelAdmin):
    list_display = ('pet', 'condition', 'date_visited', 'doctor_name', 'is_active')
    list_filter = ('is_active', 'date_visited')
    search_fields = ('pet__name', 'condition', 'diagnosis', 'doctor_name')
    readonly_fields = ('created_at', 'updated_at')