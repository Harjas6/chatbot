import { type ChangeEvent } from "react";

type FileInputProps = {
	onUpload: (files: File[]) => void;
	disabled: boolean;
};
export function FileUpload({ onUpload, disabled }: FileInputProps) {
	function handleChange(e: ChangeEvent<HTMLInputElement>) {
		e.preventDefault();
		const files = Array.from(e.currentTarget.files ?? []);
		if (files.length > 0) {
			onUpload(files);
		}
		e.currentTarget.value = "";
	}

	return (
		<div className="file-upload">
			<input
				type="file"
				accept=".pdf"
				multiple
				disabled={disabled}
				onChange={handleChange}
			/>
		</div>
	);
}
