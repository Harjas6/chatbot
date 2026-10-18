import { type SubmitEvent } from "react";

type FileInputProps = {
	onUpload: (files: File[]) => void;
	disabled: boolean;
};
export function FileUpload({ onUpload, disabled }: FileInputProps) {
	function handleSubmit(e: SubmitEvent) {
		e.preventDefault();
		const form = e.currentTarget as HTMLFormElement;
		const fileInput = form.elements[0] as HTMLInputElement;
		const files = Array.from(fileInput.files ?? []);
		if (files.length > 0) {
			onUpload(files);
		}
	}

	return (
		<div className="file-upload">
			<form onSubmit={handleSubmit}>
				<input type="file" accept=".pdf" multiple disabled={disabled} />
				<button type="submit" disabled={disabled}>
					Upload
				</button>
			</form>
		</div>
	);
}
