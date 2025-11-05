import React from "react";
import { supabase } from "@/integrations/supabase/client";

interface ProjectFile {
  id: string;
  project_id: string;
  file_name: string;
  file_type: string;
  file_url?: string;
  file_size?: number;
  is_carrier?: boolean;
  is_processed?: boolean;
  encryption_method?: string;
  created_at: string;
  user_id: string;
}

interface SteganographyOperation {
  id: string;
  project_id: string;
  activity_type: string;
  carrier_file_id?: string;
  processed_file_id?: string;
  payload_type?: string;
  encryption_enabled?: boolean;
  success?: boolean;
  error_message?: string;
  created_at: string;
  user_id: string;
}

export class ProjectFileService {
  /**
   * Store an uploaded file in the project
   */
  static async storeUploadedFile(
    projectId: string,
    file: File,
    userId: string,
    fileUrl?: string
  ): Promise<ProjectFile> {
    try {
      const fileData = {
        project_id: projectId,
        file_name: file.name,
        file_type: file.type,
        file_url: fileUrl,
        file_size: file.size,
        is_carrier: true,
        is_processed: false,
        user_id: userId
      };

      const { data, error } = await supabase
        .from('files')
        .insert([fileData])
        .select()
        .single();

      if (error) throw error;

      return data;
    } catch (error) {
      console.error('Error storing uploaded file:', error);
      throw error;
    }
  }

  /**
   * Store a processed file result in the project
   */
  static async storeProcessedFile(
    projectId: string,
    fileName: string,
    fileType: string,
    fileUrl: string,
    fileSize: number,
    userId: string,
    operationId?: string,
    encryptionMethod?: string
  ): Promise<ProjectFile> {
    try {
      const fileData = {
        project_id: projectId,
        file_name: fileName,
        file_type: fileType,
        file_url: fileUrl,
        file_size: fileSize,
        is_carrier: false,
        is_processed: true,
        encryption_method: encryptionMethod,
        user_id: userId
      };

      const { data, error } = await supabase
        .from('files')
        .insert([fileData])
        .select()
        .single();

      if (error) throw error;

      return data;
    } catch (error) {
      console.error('Error storing processed file:', error);
      throw error;
    }
  }

  /**
   * Create a steganography operation record
   */
  static async createOperation(
    projectId: string,
    userId: string,
    operationType: string,
    carrierFileId?: string,
    processedFileId?: string,
    payloadType?: string,
    encryptionEnabled: boolean = false,
    success: boolean = true,
    errorMessage?: string
  ): Promise<SteganographyOperation> {
    try {
      const operationData = {
        project_id: projectId,
        user_id: userId,
        activity_type: operationType,
        carrier_file_id: carrierFileId,
        processed_file_id: processedFileId,
        payload_type: payloadType,
        encryption_enabled: encryptionEnabled,
        success: success,
        error_message: errorMessage
      };

      const { data, error } = await supabase
        .from('activities')
        .insert([operationData])
        .select()
        .single();

      if (error) throw error;

      return data;
    } catch (error) {
      console.error('Error creating operation:', error);
      throw error;
    }
  }

  /**
   * Get all files for a project
   */
  static async getProjectFiles(projectId: string): Promise<ProjectFile[]> {
    try {
      const { data, error } = await supabase
        .from('files')
        .select('*')
        .eq('project_id', projectId)
        .order('created_at', { ascending: false });

      if (error) throw error;

      return data || [];
    } catch (error) {
      console.error('Error getting project files:', error);
      return [];
    }
  }

  /**
   * Get all operations for a project
   */
  static async getProjectOperations(projectId: string): Promise<SteganographyOperation[]> {
    try {
      const { data, error } = await supabase
        .from('activities')
        .select('*')
        .eq('project_id', projectId)
        .order('created_at', { ascending: false });

      if (error) throw error;

      return data || [];
    } catch (error) {
      console.error('Error getting project operations:', error);
      return [];
    }
  }

  /**
   * Update operation with processed file
   */
  static async updateOperationWithResult(
    operationId: string,
    processedFileId: string,
    success: boolean = true,
    errorMessage?: string
  ): Promise<void> {
    try {
      const { error } = await supabase
        .from('activities')
        .update({
          processed_file_id: processedFileId,
          success: success,
          error_message: errorMessage
        })
        .eq('id', operationId);

      if (error) throw error;
    } catch (error) {
      console.error('Error updating operation:', error);
      throw error;
    }
  }

  /**
   * Download a project file
   */
  static async downloadProjectFile(fileId: string, fileName: string): Promise<void> {
    try {
      const { data, error } = await supabase
        .from('files')
        .select('file_url')
        .eq('id', fileId)
        .single();

      if (error) throw error;

      if (data?.file_url) {
        // Create download link
        const link = document.createElement('a');
        link.href = data.file_url;
        link.download = fileName;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
      } else {
        throw new Error('File URL not found');
      }
    } catch (error) {
      console.error('Error downloading file:', error);
      throw error;
    }
  }

  /**
   * Delete a project file
   */
  static async deleteProjectFile(fileId: string): Promise<void> {
    try {
      const { error } = await supabase
        .from('files')
        .delete()
        .eq('id', fileId);

      if (error) throw error;
    } catch (error) {
      console.error('Error deleting file:', error);
      throw error;
    }
  }

  /**
   * Get file statistics for a project
   */
  static async getProjectFileStats(projectId: string): Promise<{
    totalFiles: number;
    carrierFiles: number;
    processedFiles: number;
    totalSize: number;
  }> {
    try {
      const { data, error } = await supabase
        .from('files')
        .select('is_carrier, is_processed, file_size')
        .eq('project_id', projectId);

      if (error) throw error;

      const stats = {
        totalFiles: data?.length || 0,
        carrierFiles: data?.filter(f => f.is_carrier)?.length || 0,
        processedFiles: data?.filter(f => f.is_processed)?.length || 0,
        totalSize: data?.reduce((sum, f) => sum + (f.file_size || 0), 0) || 0
      };

      return stats;
    } catch (error) {
      console.error('Error getting file stats:', error);
      return {
        totalFiles: 0,
        carrierFiles: 0,
        processedFiles: 0,
        totalSize: 0
      };
    }
  }
}