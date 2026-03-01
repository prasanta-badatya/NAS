export interface MediaFile {
  id: number;
  filename: string;
  file_size: number;
  media_type: 'image' | 'video' | 'other';
  mime_type: string;
  taken_at: string | null;
  uploaded_at: string;
  device_source: string;
  is_deleted: boolean;
  deleted_at: string | null;
  url: string;
  thumbnail_url: string | null;
}

export interface DateGroup {
  label: string;
  photos: MediaFile[];
}