import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { UploadDropzone } from "@/components/resume/UploadDropzone";

describe("UploadDropzone component", () => {
  const defaultProps = {
    selectedFile: null,
    onSelectFile: vi.fn(),
    onUpload: vi.fn(),
    isUploading: false,
    hasActiveResume: false,
    uploadSuccess: null,
    uploadError: null,
  };

  it("renders upload dropzone with prompt and browse button", () => {
    render(<UploadDropzone {...defaultProps} />);

    expect(screen.getByText("Upload Your Resume")).toBeInTheDocument();
    expect(screen.getByText(/select or drag your pdf resume/i)).toBeInTheDocument();
    expect(screen.getByText("Browse File")).toBeInTheDocument();
  });

  it("displays success message when provided", () => {
    render(
      <UploadDropzone
        {...defaultProps}
        uploadSuccess="Resume successfully parsed and matched!"
      />
    );

    expect(screen.getByText("Resume successfully parsed and matched!")).toBeInTheDocument();
  });

  it("displays error message when provided", () => {
    render(
      <UploadDropzone
        {...defaultProps}
        uploadError="Invalid file format. Please upload a PDF."
      />
    );

    expect(screen.getByText("Invalid file format. Please upload a PDF.")).toBeInTheDocument();
  });

  it("renders selected file name and upload action when file is selected", () => {
    const file = new File(["test resume content"], "my_resume.pdf", {
      type: "application/pdf",
    });

    render(<UploadDropzone {...defaultProps} selectedFile={file} />);

    expect(screen.getAllByText("my_resume.pdf").length).toBeGreaterThanOrEqual(1);
    const uploadBtn = screen.getByRole("button", { name: /upload & match/i });
    expect(uploadBtn).toBeInTheDocument();

    fireEvent.click(uploadBtn);
    expect(defaultProps.onUpload).toHaveBeenCalledWith(file);
  });
});
